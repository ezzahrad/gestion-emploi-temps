#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour restaurer les champs 'head' dans les modèles Department et Program
"""

import os
import sys
import django
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Execute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"ÉTAPE: {description}")
    print(f"{'='*60}")
    print(f"Commande: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ SUCCÈS")
            if result.stdout.strip():
                print("SORTIE:")
                print(result.stdout)
            return True
        else:
            print("❌ ERREUR")
            if result.stderr.strip():
                print("ERREUR:")
                print(result.stderr)
            if result.stdout.strip():
                print("SORTIE:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def restore_head_fields():
    """Restaure les champs head dans les modèles"""
    
    print("🔧 RESTAURATION DES CHAMPS HEAD")
    print("="*50)
    
    models_file = Path("core/models.py")
    admin_file = Path("core/admin.py")
    
    if not models_file.exists():
        print("❌ Fichier core/models.py introuvable")
        return False
    
    # Lire le contenu actuel
    with open(models_file, 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    # Vérifier si les champs head sont commentés
    if "# head = models.ForeignKey(" in models_content:
        print("📝 Restauration des champs head dans les modèles...")
        
        # Décommenter les champs head
        models_content = models_content.replace(
            "    # Champ head temporairement commenté pour éviter la dépendance circulaire\n    # head = models.ForeignKey(\n    #     'authentication.User',\n    #     on_delete=models.SET_NULL,\n    #     null=True,\n    #     blank=True,\n    #     related_name='headed_department'\n    # )",
            "    head = models.ForeignKey(\n        'authentication.User',\n        on_delete=models.SET_NULL,\n        null=True,\n        blank=True,\n        related_name='headed_department'\n    )"
        )
        
        models_content = models_content.replace(
            "    # Champ head temporairement commenté pour éviter la dépendance circulaire\n    # head = models.ForeignKey(\n    #     'authentication.User',\n    #     on_delete=models.SET_NULL,\n    #     null=True,\n    #     blank=True,\n    #     related_name='headed_program'\n    # )",
            "    head = models.ForeignKey(\n        'authentication.User',\n        on_delete=models.SET_NULL,\n        null=True,\n        blank=True,\n        related_name='headed_program'\n    )"
        )
        
        # Sauvegarder le modèle modifié
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(models_content)
        
        print("✅ Champs head restaurés dans les modèles")
        
    else:
        print("✅ Les champs head sont déjà présents dans les modèles")
    
    # Restaurer l'admin.py
    print("\n📝 Restauration de l'admin.py avec les champs head...")
    
    # Contenu admin.py complet avec champs head
    admin_content = '''from django.contrib import admin
from .models import Department, Program, Room, Subject, Teacher, Student, TeacherAvailability

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_name', 'programs_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    
    def head_name(self, obj):
        return obj.head.full_name if obj.head else 'Aucun'
    head_name.short_description = 'Chef de département'
    
    def programs_count(self, obj):
        return obj.programs.count()
    programs_count.short_description = 'Nombre de programmes'

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level', 'department', 'head_name', 'capacity', 'students_count')
    list_filter = ('level', 'department', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('department', 'level', 'name')
    
    def head_name(self, obj):
        return obj.head.full_name if obj.head else 'Aucun'
    head_name.short_description = 'Chef de programme'
    
    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'Nombre d\\'étudiants'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'room_type', 'capacity', 'department', 'is_available')
    list_filter = ('room_type', 'department', 'is_available', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('department', 'room_type', 'name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'subject_type', 'credits', 'hours_per_week', 'semester', 'department')
    list_filter = ('subject_type', 'semester', 'department', 'credits')
    search_fields = ('name', 'code')
    ordering = ('department', 'semester', 'name')
    filter_horizontal = ('program',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'employee_id', 'specialization', 'max_hours_per_week', 'is_available', 'subjects_count')
    list_filter = ('specialization', 'is_available', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'specialization')
    ordering = ('user__last_name', 'user__first_name')
    filter_horizontal = ('subjects',)
    
    def user_name(self, obj):
        return obj.user.full_name
    user_name.short_description = 'Nom'
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Nombre de matières'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'student_id', 'program', 'enrollment_year', 'is_active')
    list_filter = ('program', 'enrollment_year', 'is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'student_id')
    ordering = ('user__last_name', 'user__first_name')
    
    def user_name(self, obj):
        return obj.user.full_name
    user_name.short_description = 'Nom'

@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'day_name', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'created_at')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name')
    ordering = ('teacher', 'day_of_week', 'start_time')
    
    def teacher_name(self, obj):
        return obj.teacher.user.full_name
    teacher_name.short_description = 'Enseignant'
    
    def day_name(self, obj):
        return obj.get_day_of_week_display()
    day_name.short_description = 'Jour'
'''
    
    with open(admin_file, 'w', encoding='utf-8') as f:
        f.write(admin_content)
    
    print("✅ Admin.py restauré avec les champs head")
    
    return True

def main():
    """Fonction principale"""
    
    print("🚀 RESTAURATION DES CHAMPS HEAD - APPGET")
    print("="*60)
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("manage.py"):
        print("❌ Erreur: Ce script doit être exécuté dans le répertoire backend")
        return
    
    # Restaurer les champs head
    if not restore_head_fields():
        print("❌ Échec de la restauration des champs head")
        return
    
    # Créer les migrations
    print("\n📝 CRÉATION DES MIGRATIONS POUR LES CHAMPS HEAD")
    
    if not run_command("python manage.py makemigrations core", 
                      "Création des migrations pour les champs head"):
        print("❌ Échec de la création des migrations")
        return
    
    # Appliquer les migrations
    if not run_command("python manage.py migrate", 
                      "Application des migrations"):
        print("❌ Échec de l'application des migrations")
        return
    
    print(f"\n{'='*60}")
    print("🎉 SUCCÈS COMPLET!")
    print("Les champs 'head' ont été restaurés dans:")
    print("• Modèles Department et Program")
    print("• Interface admin Django")
    print("• Base de données (via migrations)")
    print(f"{'='*60}")
    
    print(f"\n📋 MAINTENANT VOUS POUVEZ:")
    print("1. Accéder à l'admin: http://127.0.0.1:8000/admin/")
    print("2. Créer des départements et assigner des chefs")
    print("3. Créer des programmes et assigner des responsables")
    print("4. L'erreur 'head' est définitivement résolue")

if __name__ == "__main__":
    main()
    input("\nAppuyez sur Entrée pour continuer...")
