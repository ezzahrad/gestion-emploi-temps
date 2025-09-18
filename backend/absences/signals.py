from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Absence, MakeupSession, AttendanceRecord, StudentAbsenceStatistics, AbsencePolicy
from notifications.models import Notification

@receiver(post_save, sender=Absence)
def handle_absence_created(sender, instance, created, **kwargs):
    """Gérer la création d'une nouvelle absence"""
    if created:
        # Créer une notification pour l'étudiant
        Notification.objects.create(
            recipient=instance.student,
            title="Absence enregistrée",
            message=f"Votre absence pour le cours {instance.schedule.subject_name} du {instance.absence_date.strftime('%d/%m/%Y')} a été enregistrée.",
            notification_type='absence',
            priority='medium',
            metadata={
                'absence_id': instance.id,
                'schedule_id': instance.schedule.id,
                'requires_justification': instance.absence_type == 'unjustified'
            }
        )
        
        # Notifier l'enseignant
        if instance.schedule.teacher:
            Notification.objects.create(
                recipient_id=instance.schedule.teacher,
                title="Absence déclarée",
                message=f"L'étudiant {instance.student.full_name} a déclaré une absence pour votre cours {instance.schedule.subject_name}.",
                notification_type='absence',
                priority='low',
                metadata={
                    'absence_id': instance.id,
                    'student_id': instance.student.id,
                    'schedule_id': instance.schedule.id
                }
            )
        
        # Vérifier si une justification est nécessaire
        if instance.absence_type == 'unjustified' and instance.justification_deadline:
            # Créer un rappel pour la justification
            deadline_notification = timezone.now() + timezone.timedelta(
                hours=(instance.justification_deadline - timezone.now()).total_seconds() / 3600 - 2
            )  # 2 heures avant la deadline
            
            # Note: Pour un vrai système, utiliser Celery ou Django-RQ pour programmer cette notification

@receiver(post_save, sender=Absence)
def update_absence_statistics(sender, instance, **kwargs):
    """Mettre à jour les statistiques d'absence de l'étudiant"""
    stats, created = StudentAbsenceStatistics.objects.get_or_create(
        student=instance.student
    )
    stats.calculate_statistics()

@receiver(post_save, sender=MakeupSession)
def handle_makeup_session_created(sender, instance, created, **kwargs):
    """Gérer la création d'une session de rattrapage"""
    if created:
        # Notifier l'étudiant
        Notification.objects.create(
            recipient=instance.absence.student,
            title="Session de rattrapage programmée",
            message=f"Une session de rattrapage a été programmée pour {instance.makeup_date.strftime('%d/%m/%Y')} à {instance.makeup_start_time.strftime('%H:%M')} en salle {instance.room.name}.",
            notification_type='makeup',
            priority='high',
            metadata={
                'makeup_id': instance.id,
                'absence_id': instance.absence.id,
                'makeup_date': instance.makeup_date.isoformat(),
                'room_id': instance.room.id
            }
        )
        
        # Notifier l'enseignant
        Notification.objects.create(
            recipient=instance.teacher,
            title="Session de rattrapage assignée",
            message=f"Vous avez été assigné pour une session de rattrapage avec {instance.absence.student.full_name} le {instance.makeup_date.strftime('%d/%m/%Y')}.",
            notification_type='makeup',
            priority='medium',
            metadata={
                'makeup_id': instance.id,
                'student_id': instance.absence.student.id
            }
        )

@receiver(post_save, sender=MakeupSession)
def handle_makeup_completion(sender, instance, **kwargs):
    """Gérer la finalisation d'une session de rattrapage"""
    if instance.status == 'completed':
        if instance.attendance_confirmed:
            # Notifier l'étudiant du succès
            Notification.objects.create(
                recipient=instance.absence.student,
                title="Rattrapage terminé avec succès",
                message=f"Votre session de rattrapage du {instance.makeup_date.strftime('%d/%m/%Y')} a été validée. Votre absence est maintenant rattrapée.",
                notification_type='makeup',
                priority='medium',
                metadata={
                    'makeup_id': instance.id,
                    'success': True
                }
            )
        else:
            # Notifier l'étudiant de l'échec
            Notification.objects.create(
                recipient=instance.absence.student,
                title="Rattrapage non validé",
                message=f"Votre session de rattrapage du {instance.makeup_date.strftime('%d/%m/%Y')} n'a pas été validée. Veuillez contacter votre enseignant.",
                notification_type='makeup',
                priority='high',
                metadata={
                    'makeup_id': instance.id,
                    'success': False
                }
            )

@receiver(post_save, sender=AttendanceRecord)
def handle_attendance_record(sender, instance, created, **kwargs):
    """Gérer l'enregistrement de présence"""
    if created and instance.status == 'absent':
        # Créer automatiquement une absence si elle n'existe pas
        absence, absence_created = Absence.objects.get_or_create(
            student=instance.student,
            schedule=instance.schedule,
            defaults={
                'absence_type': 'unjustified',
                'reason': 'Absence détectée automatiquement',
                'reported_by': instance.recorded_by,
                'absence_date': instance.schedule.week_start
            }
        )
        
        if absence_created:
            # Notifier l'étudiant de l'absence automatiquement détectée
            Notification.objects.create(
                recipient=instance.student,
                title="Absence automatiquement détectée",
                message=f"Une absence a été automatiquement enregistrée pour votre cours {instance.schedule.subject_name}. Si c'est une erreur, veuillez contacter votre enseignant.",
                notification_type='absence',
                priority='medium',
                metadata={
                    'absence_id': absence.id,
                    'attendance_id': instance.id,
                    'auto_detected': True
                }
            )

@receiver(post_save, sender=StudentAbsenceStatistics)
def check_absence_risk(sender, instance, **kwargs):
    """Vérifier et notifier en cas de risque d'absentéisme"""
    if instance.is_at_risk:
        priority_map = {
            'medium': 'medium',
            'high': 'high',
            'critical': 'urgent'
        }
        
        # Notifier l'étudiant
        Notification.objects.create(
            recipient=instance.student,
            title=f"Alerte absentéisme - Niveau {instance.get_risk_level_display()}",
            message=f"Votre taux d'absence ({instance.absence_rate:.1f}%) nécessite votre attention. Consultez vos statistiques et planifiez vos rattrapages.",
            notification_type='system',
            priority=priority_map.get(instance.risk_level, 'medium'),
            metadata={
                'absence_rate': float(instance.absence_rate),
                'risk_level': instance.risk_level,
                'total_absences': instance.total_absences
            }
        )
        
        # Notifier l'administration si critique
        if instance.risk_level == 'critical':
            from authentication.models import User
            admins = User.objects.filter(role__in=['admin', 'department_head'])
            
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    title="Étudiant à risque critique",
                    message=f"L'étudiant {instance.student.full_name} présente un taux d'absence critique ({instance.absence_rate:.1f}%). Intervention nécessaire.",
                    notification_type='system',
                    priority='urgent',
                    metadata={
                        'student_id': instance.student.id,
                        'absence_rate': float(instance.absence_rate),
                        'risk_level': instance.risk_level
                    }
                )
