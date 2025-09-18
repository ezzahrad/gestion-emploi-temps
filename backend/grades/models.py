from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Subject, Program
from decimal import Decimal

User = get_user_model()

class GradeScale(models.Model):
    """Configuration des échelles de notation"""
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    # Échelle de notation
    a_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('95.00'))
    a_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('90.00'))
    b_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('85.00'))
    b_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('80.00'))
    c_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('75.00'))
    c_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('70.00'))
    d_plus_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('65.00'))
    d_min = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('60.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            # S'assurer qu'il n'y a qu'une seule échelle par défaut
            GradeScale.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def get_letter_grade(self, percentage):
        """Convertir un pourcentage en note lettrée"""
        if percentage >= self.a_plus_min:
            return 'A+'
        elif percentage >= self.a_min:
            return 'A'
        elif percentage >= self.b_plus_min:
            return 'B+'
        elif percentage >= self.b_min:
            return 'B'
        elif percentage >= self.c_plus_min:
            return 'C+'
        elif percentage >= self.c_min:
            return 'C'
        elif percentage >= self.d_plus_min:
            return 'D+'
        elif percentage >= self.d_min:
            return 'D'
        else:
            return 'F'

    def __str__(self):
        return self.name

class Evaluation(models.Model):
    """Types d'évaluation configurables"""
    EVALUATION_TYPE_CHOICES = (
        ('exam', 'Examen'),
        ('quiz', 'Quiz'),
        ('homework', 'Devoir'),
        ('project', 'Projet'),
        ('participation', 'Participation'),
        ('final', 'Examen final'),
        ('midterm', 'Examen de mi-parcours'),
        ('presentation', 'Présentation'),
        ('lab_work', 'Travail de laboratoire'),
    )
    
    name = models.CharField(max_length=100)
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='evaluations')
    max_grade = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.00'))
    coefficient = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.00'))
    evaluation_date = models.DateTimeField()
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_evaluations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"{self.name} - {self.subject.name}"

class Grade(models.Model):
    """Notes des étudiants"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='grades')
    grade_value = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Champs calculés automatiquement
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    grade_letter = models.CharField(max_length=2, blank=True)
    
    comments = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    graded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='graded_evaluations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'evaluation']
        ordering = ['-evaluation__evaluation_date']

    def save(self, *args, **kwargs):
        # Calculer le pourcentage
        if self.evaluation.max_grade > 0:
            self.percentage = (self.grade_value / self.evaluation.max_grade) * 100
        
        # Calculer la note lettrée
        grade_scale = GradeScale.objects.filter(is_default=True).first()
        if grade_scale:
            self.grade_letter = grade_scale.get_letter_grade(float(self.percentage))
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.evaluation.name}: {self.grade_value}/{self.evaluation.max_grade}"

class SubjectGradeSummary(models.Model):
    """Résumé des notes par matière pour chaque étudiant"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_summaries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_summaries')
    
    # Moyennes calculées
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weighted_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_letter = models.CharField(max_length=2, blank=True)
    
    # Statistiques
    total_evaluations = models.IntegerField(default=0)
    published_evaluations = models.IntegerField(default=0)
    total_coefficient = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='validated_summaries'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['subject__name']

    def calculate_averages(self):
        """Calculer les moyennes pour cette matière"""
        grades = self.student.grades.filter(
            evaluation__subject=self.subject,
            is_published=True
        )
        
        if not grades.exists():
            return
        
        # Moyenne simple
        total_points = sum(grade.grade_value for grade in grades)
        self.average_grade = total_points / grades.count()
        
        # Moyenne pondérée
        total_weighted_points = sum(
            grade.grade_value * grade.evaluation.coefficient 
            for grade in grades
        )
        total_coefficients = sum(
            grade.evaluation.coefficient 
            for grade in grades
        )
        
        if total_coefficients > 0:
            self.weighted_average = total_weighted_points / total_coefficients
        
        # Note lettrée
        grade_scale = GradeScale.objects.filter(is_default=True).first()
        if grade_scale and self.weighted_average:
            # Convertir en pourcentage (supposant que la note max est 20)
            percentage = (float(self.weighted_average) / 20) * 100
            self.grade_letter = grade_scale.get_letter_grade(percentage)
        
        # Statistiques
        self.total_evaluations = self.student.grades.filter(evaluation__subject=self.subject).count()
        self.published_evaluations = grades.count()
        self.total_coefficient = total_coefficients
        
        self.save()

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}: {self.weighted_average or 'N/A'}"

class StudentTranscript(models.Model):
    """Relevé de notes d'un étudiant"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcripts')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=9)  # ex: "2024-2025"
    
    # Moyennes générales
    overall_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    grade_letter = models.CharField(max_length=2, blank=True)
    
    # Crédits
    total_credits = models.IntegerField(default=0)
    acquired_credits = models.IntegerField(default=0)
    
    # Classement
    rank = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(null=True, blank=True)
    
    # Statut
    is_finalized = models.BooleanField(default=False)
    finalized_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='finalized_transcripts'
    )
    finalized_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'program', 'semester', 'academic_year']
        ordering = ['-academic_year', '-semester']

    def calculate_gpa(self):
        """Calculer le GPA selon le système américain"""
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'B+': 3.5, 'B': 3.0, 
            'C+': 2.5, 'C': 2.0, 'D+': 1.5, 'D': 1.0, 'F': 0.0
        }
        
        summaries = self.student.subject_summaries.filter(
            subject__program=self.program,
            is_validated=True
        )
        
        total_grade_points = 0
        total_credits = 0
        
        for summary in summaries:
            credits = summary.subject.credits
            grade_point = grade_points.get(summary.grade_letter, 0.0)
            
            total_grade_points += grade_point * credits
            total_credits += credits
        
        if total_credits > 0:
            self.gpa = Decimal(str(total_grade_points / total_credits))
            self.total_credits = total_credits
        
        self.save()

    def __str__(self):
        return f"{self.student.full_name} - {self.program.name} S{self.semester} {self.academic_year}"
