from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from datetime import timedelta
from schedule.models import Schedule

User = get_user_model()

class AbsencePolicy(models.Model):
    """Politique de gestion des absences"""
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    # Limites d'absence
    max_unjustified_absences = models.IntegerField(default=3, help_text="Nombre maximum d'absences non justifiées")
    max_total_absences_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=25.0, help_text="Pourcentage maximum d'absences totales")
    
    # Délais
    justification_deadline_hours = models.IntegerField(default=48, help_text="Délai en heures pour justifier une absence")
    makeup_request_deadline_days = models.IntegerField(default=7, help_text="Délai en jours pour demander un rattrapage")
    
    # Règles de justification
    medical_justification_required = models.BooleanField(default=True)
    family_emergency_accepted = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            # S'assurer qu'il n'y a qu'une seule politique par défaut
            AbsencePolicy.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Absence(models.Model):
    """Enregistrement d'une absence"""
    ABSENCE_TYPE_CHOICES = (
        ('unjustified', 'Non justifiée'),
        ('medical', 'Médicale'),
        ('family', 'Familiale'),
        ('personal', 'Personnelle'),
        ('transportation', 'Transport'),
        ('other', 'Autre'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
        ('auto_approved', 'Auto-approuvée'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='absences')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='absences')
    
    # Type et raison
    absence_type = models.CharField(max_length=20, choices=ABSENCE_TYPE_CHOICES, default='unjustified')
    reason = models.TextField(help_text="Raison détaillée de l'absence")
    
    # Justification
    justification_document = models.FileField(
        upload_to='justifications/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        help_text="Document justificatif (PDF, image ou document Word)"
    )
    
    # Statut et approbation
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    is_makeup_required = models.BooleanField(default=False)
    makeup_completed = models.BooleanField(default=False)
    
    # Métadonnées
    reported_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='absence_app_reported_absences',
        help_text="Qui a signalé l'absence (étudiant ou enseignant)"
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='absence_app_approved_absences'
    )
    
    # Dates importantes
    absence_date = models.DateField()
    reported_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    justification_deadline = models.DateTimeField(null=True, blank=True)
    
    # Commentaires
    admin_comments = models.TextField(blank=True, help_text="Commentaires de l'administration")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-absence_date', '-created_at']
        unique_together = ['student', 'schedule']

    def save(self, *args, **kwargs):
        if not self.absence_date:
            # Extraire la date du planning
            self.absence_date = self.schedule.week_start
        
        if not self.justification_deadline:
            # Calculer la deadline de justification
            policy = AbsencePolicy.objects.filter(is_default=True).first()
            if policy:
                hours = policy.justification_deadline_hours
                self.justification_deadline = self.reported_at + timedelta(hours=hours)
        
        super().save(*args, **kwargs)

    def is_justification_overdue(self):
        """Vérifier si la deadline de justification est dépassée"""
        if self.justification_deadline:
            return timezone.now() > self.justification_deadline
        return False

    def can_request_makeup(self):
        """Vérifier si un rattrapage peut être demandé"""
        if self.makeup_completed or not self.is_makeup_required:
            return False
        
        policy = AbsencePolicy.objects.filter(is_default=True).first()
        if policy:
            deadline = self.absence_date + timedelta(days=policy.makeup_request_deadline_days)
            return timezone.now().date() <= deadline
        
        return True

    def get_schedule_details(self):
        """Obtenir les détails du cours manqué"""
        return {
            'subject_name': self.schedule.subject_name,
            'teacher_name': self.schedule.teacher_name,
            'room_name': self.schedule.room_name,
            'date': self.schedule.week_start.strftime('%d/%m/%Y'),
            'start_time': self.schedule.start_time,
            'end_time': self.schedule.end_time,
            'day_name': self.schedule.day_name
        }

    def __str__(self):
        return f"{self.student.full_name} - {self.schedule.subject_name} - {self.absence_date}"

class MakeupSession(models.Model):
    """Session de rattrapage"""
    STATUS_CHOICES = (
        ('scheduled', 'Programmée'),
        ('confirmed', 'Confirmée'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('rescheduled', 'Reprogrammée'),
    )
    
    absence = models.OneToOneField(Absence, on_delete=models.CASCADE, related_name='makeup_session')
    
    # Détails de la session de rattrapage
    makeup_date = models.DateField()
    makeup_start_time = models.TimeField()
    makeup_end_time = models.TimeField()
    
    # Lieu et enseignant
    room = models.ForeignKey('core.Room', on_delete=models.CASCADE, related_name='absence_app_makeup_sessions')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='absence_app_makeup_sessions')
    
    # Statut et suivi
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    attendance_confirmed = models.BooleanField(default=False)
    
    # Commentaires et notes
    session_notes = models.TextField(blank=True, help_text="Notes de la session de rattrapage")
    student_feedback = models.TextField(blank=True, help_text="Retour de l'étudiant")
    teacher_feedback = models.TextField(blank=True, help_text="Retour de l'enseignant")
    
    # Évaluation du rattrapage
    makeup_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_successful = models.BooleanField(null=True, blank=True)
    
    # Métadonnées
    scheduled_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='absence_app_scheduled_makeups'
    )
    confirmed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='absence_app_confirmed_makeups'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-makeup_date', '-makeup_start_time']

    def save(self, *args, **kwargs):
        # Marquer l'absence comme ayant un rattrapage
        if self.pk is None:  # Nouvelle session
            self.absence.is_makeup_required = True
            self.absence.save()
        
        super().save(*args, **kwargs)

    def mark_completed(self, teacher_feedback="", attendance_confirmed=True):
        """Marquer la session comme terminée"""
        self.status = 'completed'
        self.attendance_confirmed = attendance_confirmed
        self.teacher_feedback = teacher_feedback
        self.confirmed_at = timezone.now()
        
        if attendance_confirmed:
            self.absence.makeup_completed = True
            self.absence.save()
        
        self.save()

    def get_duration_minutes(self):
        """Calculer la durée en minutes"""
        if self.makeup_start_time and self.makeup_end_time:
            start = timezone.datetime.combine(timezone.now().date(), self.makeup_start_time)
            end = timezone.datetime.combine(timezone.now().date(), self.makeup_end_time)
            return int((end - start).total_seconds() / 60)
        return 0

    def __str__(self):
        return f"Rattrapage - {self.absence.student.full_name} - {self.makeup_date}"

class AttendanceRecord(models.Model):
    """Enregistrement de présence détaillé"""
    STATUS_CHOICES = (
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('late', 'En retard'),
        ('excused', 'Excusé'),
        ('left_early', 'Parti tôt'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendance_records')
    
    # Statut de présence
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='present')
    
    # Heures précises
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    
    # Minutes de retard/départ anticipé
    minutes_late = models.IntegerField(default=0)
    minutes_early_departure = models.IntegerField(default=0)
    
    # Commentaires
    notes = models.TextField(blank=True)
    
    # Qui a enregistré la présence
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='absence_app_recorded_attendances')
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Validation
    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='absence_app_validated_attendances'
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-schedule__week_start', 'schedule__start_time']
        unique_together = ['student', 'schedule']

    def calculate_lateness(self):
        """Calculer le retard en minutes"""
        if self.arrival_time and self.status in ['late', 'present']:
            scheduled_start = self.schedule.start_time
            if self.arrival_time > scheduled_start:
                scheduled_datetime = timezone.datetime.combine(timezone.now().date(), scheduled_start)
                arrival_datetime = timezone.datetime.combine(timezone.now().date(), self.arrival_time)
                self.minutes_late = int((arrival_datetime - scheduled_datetime).total_seconds() / 60)
            else:
                self.minutes_late = 0

    def calculate_early_departure(self):
        """Calculer le départ anticipé en minutes"""
        if self.departure_time and self.status in ['left_early', 'present']:
            scheduled_end = self.schedule.end_time
            if self.departure_time < scheduled_end:
                scheduled_datetime = timezone.datetime.combine(timezone.now().date(), scheduled_end)
                departure_datetime = timezone.datetime.combine(timezone.now().date(), self.departure_time)
                self.minutes_early_departure = int((scheduled_datetime - departure_datetime).total_seconds() / 60)
            else:
                self.minutes_early_departure = 0

    def save(self, *args, **kwargs):
        self.calculate_lateness()
        self.calculate_early_departure()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.schedule.subject_name} - {self.status}"

class StudentAbsenceStatistics(models.Model):
    """Statistiques d'absence par étudiant (calculées périodiquement)"""
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='absence_app_statistics')
    
    # Compteurs d'absences
    total_absences = models.IntegerField(default=0)
    justified_absences = models.IntegerField(default=0)
    unjustified_absences = models.IntegerField(default=0)
    pending_absences = models.IntegerField(default=0)
    
    # Pourcentages
    absence_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    justified_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Rattrapages
    pending_makeups = models.IntegerField(default=0)
    completed_makeups = models.IntegerField(default=0)
    failed_makeups = models.IntegerField(default=0)
    
    # Statut de risque
    is_at_risk = models.BooleanField(default=False)
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
            ('critical', 'Critique')
        ],
        default='low'
    )
    
    # Dernière mise à jour
    last_calculated = models.DateTimeField(auto_now=True)
    period_start = models.DateField()
    period_end = models.DateField()

    def calculate_statistics(self, start_date=None, end_date=None):
        """Calculer les statistiques d'absence"""
        if not start_date:
            start_date = timezone.now().date().replace(month=9, day=1)  # Début année scolaire
        if not end_date:
            end_date = timezone.now().date()
        
        # Absences dans la période
        absences = self.student.absences.filter(
            absence_date__range=[start_date, end_date]
        )
        
        self.total_absences = absences.count()
        self.justified_absences = absences.filter(
            status__in=['approved', 'auto_approved']
        ).count()
        self.unjustified_absences = absences.filter(
            absence_type='unjustified'
        ).count()
        self.pending_absences = absences.filter(status='pending').count()
        
        # Calcul des taux
        total_courses = self.student.attendance_records.filter(
            schedule__week_start__range=[start_date, end_date]
        ).count()
        
        if total_courses > 0:
            self.absence_rate = (self.total_absences / total_courses) * 100
            if self.total_absences > 0:
                self.justified_rate = (self.justified_absences / self.total_absences) * 100
        
        # Rattrapages
        makeups = MakeupSession.objects.filter(
            absence__student=self.student,
            makeup_date__range=[start_date, end_date]
        )
        
        self.pending_makeups = makeups.filter(status='scheduled').count()
        self.completed_makeups = makeups.filter(status='completed').count()
        self.failed_makeups = makeups.filter(status='cancelled').count()
        
        # Évaluation du risque
        self.calculate_risk_level()
        
        self.period_start = start_date
        self.period_end = end_date
        self.save()

    def calculate_risk_level(self):
        """Calculer le niveau de risque"""
        policy = AbsencePolicy.objects.filter(is_default=True).first()
        
        if policy:
            # Risque basé sur les absences non justifiées
            if self.unjustified_absences >= policy.max_unjustified_absences:
                self.risk_level = 'critical'
                self.is_at_risk = True
            elif self.absence_rate >= policy.max_total_absences_percentage:
                self.risk_level = 'high'
                self.is_at_risk = True
            elif self.absence_rate >= (policy.max_total_absences_percentage * 0.7):
                self.risk_level = 'medium'
                self.is_at_risk = True
            else:
                self.risk_level = 'low'
                self.is_at_risk = False

    def __str__(self):
        return f"{self.student.full_name} - Absences: {self.total_absences} ({self.absence_rate:.1f}%)"
