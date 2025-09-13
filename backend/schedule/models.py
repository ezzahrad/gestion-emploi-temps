from django.db import models
from django.contrib.auth import get_user_model
from core.models import Program, Room, Subject, Teacher

User = get_user_model()

class Schedule(models.Model):
    DAY_CHOICES = (
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
    )
    
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='schedules')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    week_start = models.DateField(help_text="Date du début de la semaine")
    week_end = models.DateField(help_text="Date de fin de la semaine")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Check for time conflicts
        if self.start_time >= self.end_time:
            raise ValidationError('L\'heure de début doit être antérieure à l\'heure de fin.')
        
        # Check for room conflicts
        room_conflicts = Schedule.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            week_start=self.week_start,
            week_end=self.week_end,
            is_active=True
        ).exclude(id=self.id if self.id else None)
        
        for conflict in room_conflicts:
            if (self.start_time < conflict.end_time and self.end_time > conflict.start_time):
                raise ValidationError(f'Conflit de salle avec {conflict.title}')
        
        # Check for teacher conflicts
        teacher_conflicts = Schedule.objects.filter(
            teacher=self.teacher,
            day_of_week=self.day_of_week,
            week_start=self.week_start,
            week_end=self.week_end,
            is_active=True
        ).exclude(id=self.id if self.id else None)
        
        for conflict in teacher_conflicts:
            if (self.start_time < conflict.end_time and self.end_time > conflict.start_time):
                raise ValidationError(f'Conflit enseignant avec {conflict.title}')

class Absence(models.Model):
    ABSENCE_TYPE_CHOICES = (
        ('teacher', 'Absence Enseignant'),
        ('student', 'Absence Étudiant'),
        ('room', 'Indisponibilité Salle'),
    )
    
    REASON_CHOICES = (
        ('sick', 'Maladie'),
        ('personal', 'Personnel'),
        ('official', 'Mission Officielle'),
        ('maintenance', 'Maintenance'),
        ('other', 'Autre'),
    )
    
    absence_type = models.CharField(max_length=20, choices=ABSENCE_TYPE_CHOICES)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='absences')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, related_name='absences')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True, related_name='absences')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_absences')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_absences')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_absence_type_display()} - {self.start_datetime.strftime('%d/%m/%Y')}"

class MakeupSession(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En Attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('completed', 'Terminé'),
    )
    
    original_schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='makeup_sessions')
    absence = models.ForeignKey(Absence, on_delete=models.CASCADE, related_name='makeup_sessions')
    new_datetime = models.DateTimeField()
    new_room = models.ForeignKey(Room, on_delete=models.CASCADE)
    duration_hours = models.DecimalField(max_digits=3, decimal_places=1, default=1.5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_makeups')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_makeups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rattrapage - {self.original_schedule.title} - {self.new_datetime.strftime('%d/%m/%Y %H:%M')}"