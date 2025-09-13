from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur Pédagogique'),
        ('department_head', 'Chef de Département'),
        ('program_head', 'Chef de Filière'), 
        ('teacher', 'Enseignant'),
        ('student', 'Étudiant'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # TEMPORAIREMENT COMMENTÉ - À RESTAURER APRÈS
    # department = models.ForeignKey('core.Department', on_delete=models.SET_NULL, null=True, blank=True)
    # program = models.ForeignKey('core.Program', on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
