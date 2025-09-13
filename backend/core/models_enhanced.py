# models.py - Version améliorée pour AppGET
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_department'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"


class Program(models.Model):
    LEVEL_CHOICES = (
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'), 
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('D1', 'Doctorat 1'),
        ('D2', 'Doctorat 2'),
        ('D3', 'Doctorat 3'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_program'
    )
    capacity = models.PositiveIntegerField(default=30)
    color_code = models.CharField(max_length=7, default='#3B82F6', help_text="Code couleur hexadécimal")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"

    class Meta:
        verbose_name = "Filière/Programme"
        verbose_name_plural = "Filières/Programmes"
        unique_together = ('department', 'level', 'name')


class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('amphitheater', 'Amphithéâtre'),
        ('lecture', 'Salle de Cours'),
        ('td', 'Salle de TD'),
        ('lab', 'Laboratoire/TP'),
        ('computer_lab', 'Salle Informatique'),
        ('conference', 'Salle de Conférence'),
        ('library', 'Bibliothèque'),
        ('other', 'Autre'),
    )

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    building = models.CharField(max_length=100, blank=True, help_text="Nom du bâtiment")
    floor = models.CharField(max_length=10, blank=True, help_text="Étage")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms')
    equipment = models.TextField(blank=True, help_text="Équipements disponibles (séparés par des virgules)")
    location_details = models.TextField(blank=True, help_text="Détails de localisation")
    is_available = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)],
                                   help_text="Priorité d'utilisation (1=faible, 10=élevée)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()}) - Cap. {self.capacity}"

    @property
    def equipment_list(self):
        """Retourne la liste des équipements"""
        return [eq.strip() for eq in self.equipment.split(',') if eq.strip()] if self.equipment else []

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"


class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = (
        ('lecture', 'Cours Magistral'),
        ('td', 'Travaux Dirigés'),
        ('tp', 'Travaux Pratiques'),
        ('exam', 'Examen'),
        ('conference', 'Conférence'),
        ('seminar', 'Séminaire'),
        ('workshop', 'Atelier'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    programs = models.ManyToManyField(Program, related_name='subjects')
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPE_CHOICES)
    credits = models.PositiveIntegerField(default=3)
    hours_per_week = models.PositiveIntegerField(default=3)
    total_hours = models.PositiveIntegerField(default=42, help_text="Total d'heures dans le semestre")
    semester = models.PositiveIntegerField(choices=[(1, 'Semestre 1'), (2, 'Semestre 2')])
    required_equipment = models.TextField(blank=True, help_text="Équipements requis")
    min_room_capacity = models.PositiveIntegerField(default=30, help_text="Capacité minimale de salle requise")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def required_equipment_list(self):
        """Retourne la liste des équipements requis"""
        return [eq.strip() for eq in self.required_equipment.split(',') if eq.strip()] if self.required_equipment else []

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"


class Teacher(models.Model):
    TEACHER_TYPE_CHOICES = (
        ('professor', 'Professeur'),
        ('associate', 'Professeur Associé'),
        ('assistant', 'Professeur Assistant'),
        ('lecturer', 'Chargé de Cours'),
        ('visitor', 'Professeur Invité'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    teacher_type = models.CharField(max_length=20, choices=TEACHER_TYPE_CHOICES, default='lecturer')
    specialization = models.CharField(max_length=200)
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)
    departments = models.ManyToManyField(Department, related_name='teachers', blank=True)
    max_hours_per_week = models.PositiveIntegerField(default=20)
    max_hours_per_day = models.PositiveIntegerField(default=6)
    preferred_time_slots = models.TextField(blank=True, help_text="Créneaux préférés (JSON)")
    unavailable_slots = models.TextField(blank=True, help_text="Créneaux non disponibles (JSON)")
    office_location = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    is_external = models.BooleanField(default=False, help_text="Enseignant externe")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_teacher_type_display()})"

    @property
    def preferred_slots(self):
        """Retourne les créneaux préférés sous forme de liste"""
        try:
            return json.loads(self.preferred_time_slots) if self.preferred_time_slots else []
        except:
            return []

    @property
    def unavailable_slots_list(self):
        """Retourne les créneaux non disponibles sous forme de liste"""
        try:
            return json.loads(self.unavailable_slots) if self.unavailable_slots else []
        except:
            return []

    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='students')
    enrollment_year = models.PositiveIntegerField()
    academic_year = models.CharField(max_length=9, help_text="Ex: 2024-2025")
    group_name = models.CharField(max_length=50, blank=True, help_text="Nom du groupe/classe")
    is_active = models.BooleanField(default=True)
    is_repeating = models.BooleanField(default=False, help_text="Étudiant redoublant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        unique_together = ('program', 'student_id')


class TimeSlot(models.Model):
    """Créneaux horaires disponibles"""
    DAY_CHOICES = (
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    )

    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    name = models.CharField(max_length=100, help_text="Ex: Créneau 1, Matinée, etc.")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, help_text="Priorité du créneau (1=faible, 10=élevée)")

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    @property
    def duration_minutes(self):
        """Durée du créneau en minutes"""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)

    class Meta:
        verbose_name = "Créneau Horaire"
        verbose_name_plural = "Créneaux Horaires"
        unique_together = ('day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']


class Schedule(models.Model):
    """Emploi du temps - version améliorée"""
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='schedules')
    programs = models.ManyToManyField(Program, related_name='schedules')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedules')
    
    # Dates spécifiques
    start_date = models.DateField(help_text="Date de début de cette session")
    end_date = models.DateField(help_text="Date de fin de cette session")
    
    # Métadonnées
    session_number = models.PositiveIntegerField(default=1, help_text="Numéro de la séance")
    total_sessions = models.PositiveIntegerField(default=14, help_text="Nombre total de séances prévues")
    duration_minutes = models.PositiveIntegerField(default=90, help_text="Durée en minutes")
    
    # États
    is_active = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    is_makeup = models.BooleanField(default=False, help_text="Séance de rattrapage")
    
    # Informations complémentaires
    notes = models.TextField(blank=True)
    required_students = models.PositiveIntegerField(null=True, blank=True, help_text="Nombre d'étudiants attendus")
    
    # Métadonnées de gestion
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Séance d'Emploi du Temps"
        verbose_name_plural = "Séances d'Emploi du Temps"
        ordering = ['start_date', 'time_slot__start_time']

    def __str__(self):
        return f"{self.subject.name} - {self.teacher.user.get_full_name()} - {self.start_date}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Vérifier que la date de fin >= date de début
        if self.end_date < self.start_date:
            raise ValidationError('La date de fin doit être postérieure à la date de début.')
        
        # Vérifier les conflits de salles
        room_conflicts = Schedule.objects.filter(
            room=self.room,
            time_slot=self.time_slot,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            is_active=True,
            is_cancelled=False
        ).exclude(id=self.id if self.id else None)
        
        if room_conflicts.exists():
            raise ValidationError(f'Conflit de salle détecté avec: {room_conflicts.first().title}')
        
        # Vérifier les conflits d'enseignants
        teacher_conflicts = Schedule.objects.filter(
            teacher=self.teacher,
            time_slot=self.time_slot,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            is_active=True,
            is_cancelled=False
        ).exclude(id=self.id if self.id else None)
        
        if teacher_conflicts.exists():
            raise ValidationError(f'Conflit enseignant détecté avec: {teacher_conflicts.first().title}')

    @property
    def student_count(self):
        """Nombre d'étudiants concernés par cette séance"""
        return sum([program.students.filter(is_active=True).count() for program in self.programs.all()])

    @property
    def is_room_suitable(self):
        """Vérifie si la salle est adaptée"""
        return self.room.capacity >= self.student_count


class ExcelImportLog(models.Model):
    """Journal des importations Excel"""
    STATUS_CHOICES = (
        ('pending', 'En cours'),
        ('success', 'Réussi'),
        ('failed', 'Échoué'),
        ('partial', 'Partiel'),
    )

    filename = models.CharField(max_length=255)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Statistiques
    total_rows = models.PositiveIntegerField(default=0)
    successful_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    
    # Détails
    error_log = models.TextField(blank=True)
    success_log = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Temps de traitement en secondes")

    class Meta:
        verbose_name = "Journal d'Import Excel"
        verbose_name_plural = "Journaux d'Import Excel"
        ordering = ['-import_date']

    def __str__(self):
        return f"{self.filename} - {self.get_status_display()}"


class TimetableGeneration(models.Model):
    """Journal des générations d'emploi du temps"""
    STATUS_CHOICES = (
        ('pending', 'En cours'),
        ('success', 'Réussi'),
        ('failed', 'Échoué'),
        ('optimizing', 'Optimisation'),
    )

    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Paramètres
    start_date = models.DateField()
    end_date = models.DateField()
    programs = models.ManyToManyField(Program, blank=True)
    
    # Résultats
    total_sessions_planned = models.PositiveIntegerField(default=0)
    conflicts_resolved = models.PositiveIntegerField(default=0)
    optimization_score = models.FloatField(null=True, blank=True, help_text="Score d'optimisation (0-100)")
    
    # Logs
    execution_log = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Temps de génération en secondes")

    class Meta:
        verbose_name = "Génération d'Emploi du Temps"
        verbose_name_plural = "Générations d'Emploi du Temps"
        ordering = ['-generation_date']

    def __str__(self):
        return f"Génération {self.id} - {self.get_status_display()}"
