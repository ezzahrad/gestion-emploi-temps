from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Grade, SubjectGradeSummary, Evaluation
from notifications.models import Notification

@receiver(post_save, sender=Grade)
def update_subject_summary_on_grade_save(sender, instance, created, **kwargs):
    """Mettre à jour le résumé de la matière quand une note est ajoutée/modifiée"""
    summary, created_summary = SubjectGradeSummary.objects.get_or_create(
        student=instance.student,
        subject=instance.evaluation.subject
    )
    summary.calculate_averages()
    
    # Créer une notification si la note est publiée
    if instance.is_published and created:
        Notification.objects.create(
            recipient=instance.student,
            title="Nouvelle note disponible",
            message=f"Votre note pour {instance.evaluation.name} ({instance.evaluation.subject.name}) est maintenant disponible: {instance.grade_value}/{instance.evaluation.max_grade}",
            notification_type='grade',
            priority='medium',
            metadata={
                'grade_id': instance.id,
                'evaluation_id': instance.evaluation.id,
                'subject_id': instance.evaluation.subject.id
            }
        )

@receiver(post_delete, sender=Grade)
def update_subject_summary_on_grade_delete(sender, instance, **kwargs):
    """Mettre à jour le résumé de la matière quand une note est supprimée"""
    try:
        summary = SubjectGradeSummary.objects.get(
            student=instance.student,
            subject=instance.evaluation.subject
        )
        summary.calculate_averages()
    except SubjectGradeSummary.DoesNotExist:
        pass

@receiver(post_save, sender=Evaluation)
def notify_students_new_evaluation(sender, instance, created, **kwargs):
    """Notifier les étudiants quand une nouvelle évaluation est créée"""
    if created:
        # Obtenir tous les étudiants du programme de la matière
        from authentication.models import User
        students = User.objects.filter(
            role='student',
            program__in=instance.subject.program.all()
        )
        
        notifications = []
        for student in students:
            notifications.append(
                Notification(
                    recipient=student,
                    title="Nouvelle évaluation programmée",
                    message=f"Une nouvelle évaluation '{instance.name}' a été programmée pour {instance.subject.name} le {instance.evaluation_date.strftime('%d/%m/%Y')}",
                    notification_type='reminder',
                    priority='medium',
                    metadata={
                        'evaluation_id': instance.id,
                        'subject_id': instance.subject.id,
                        'evaluation_date': instance.evaluation_date.isoformat()
                    }
                )
            )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
