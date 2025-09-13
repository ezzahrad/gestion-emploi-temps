from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_department'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    LEVEL_CHOICES = (
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    head = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_program'
    )
    capacity = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"


class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('lecture', 'Salle de Cours'),
        ('td', 'Salle de TD'),
        ('lab', 'Laboratoire/TP'),
        ('amphitheater', 'Amphithéâtre'),
    )

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms')
    equipment = models.TextField(blank=True, help_text="Équipements disponibles")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"


class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = (
        ('lecture', 'Cours Magistral'),
        ('td', 'Travaux Dirigés'),
        ('lab', 'Travaux Pratiques'),
        ('exam', 'Examen'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    program = models.ManyToManyField(Program, related_name='subjects')
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPE_CHOICES)
    credits = models.PositiveIntegerField(default=3)
    hours_per_week = models.PositiveIntegerField(default=3)
    semester = models.PositiveIntegerField(choices=[(1, '1'), (2, '2')])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Teacher(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=200)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    max_hours_per_week = models.PositiveIntegerField(default=20)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.full_name


class Student(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='students')
    enrollment_year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.student_id}"


class TeacherAvailability(models.Model):
    DAY_CHOICES = (
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
    )

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.teacher} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
