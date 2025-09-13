# create_test_data.py - Script pour créer des données de test
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appget.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import *
from datetime import time, date, timedelta

def create_test_data():
    print("🎯 Création des données de test...")
    
    # 1. Créer des départements
    dept_info = Department.objects.create(
        name="Informatique",
        code="INFO",
        description="Département d'Informatique et Sciences du Numérique"
    )
    
    dept_math = Department.objects.create(
        name="Mathématiques", 
        code="MATH",
        description="Département de Mathématiques"
    )
    
    print("✅ Départements créés")
    
    # 2. Créer des programmes
    prog_l3_info = Program.objects.create(
        name="Licence Informatique",
        code="L3-INFO",
        level="L3",
        duration_years=3,
        max_students=50,
        department=dept_info
    )
    
    prog_m1_info = Program.objects.create(
        name="Master Informatique",
        code="M1-INFO", 
        level="M1",
        duration_years=2,
        max_students=30,
        department=dept_info
    )
    
    print("✅ Programmes créés")
    
    # 3. Créer des salles
    Room.objects.create(
        name="Amphi A",
        code="AMPH-A",
        room_type="amphitheater",
        capacity=200,
        building="Bâtiment Principal",
        floor="RDC",
        equipment="Projecteur, Micro, Climatisation",
        department=dept_info
    )
    
    Room.objects.create(
        name="Salle TD-01",
        code="TD-01",
        room_type="classroom", 
        capacity=30,
        building="Bâtiment A",
        floor="1er étage",
        equipment="Tableau, Projecteur",
        department=dept_info
    )
    
    Room.objects.create(
        name="Labo Info",
        code="LAB-01",
        room_type="laboratory",
        capacity=25,
        building="Bâtiment B",
        floor="RDC", 
        equipment="PC, Serveur, Réseau",
        department=dept_info
    )
    
    print("✅ Salles créées")
    
    # 4. Créer des créneaux horaires
    time_slots = [
        (0, time(8, 0), time(9, 30)),   # Lundi 8h-9h30
        (0, time(10, 0), time(11, 30)), # Lundi 10h-11h30
        (0, time(14, 0), time(15, 30)), # Lundi 14h-15h30
        (1, time(8, 0), time(9, 30)),   # Mardi 8h-9h30
        (1, time(10, 0), time(11, 30)), # Mardi 10h-11h30
        (2, time(8, 0), time(9, 30)),   # Mercredi 8h-9h30
        (3, time(14, 0), time(15, 30)), # Jeudi 14h-15h30
        (4, time(8, 0), time(9, 30)),   # Vendredi 8h-9h30
    ]
    
    for day, start, end in time_slots:
        duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
        TimeSlot.objects.create(
            day_of_week=day,
            start_time=start,
            end_time=end, 
            duration_minutes=duration
        )
    
    print("✅ Créneaux horaires créés")
    
    # 5. Créer des matières
    Subject.objects.create(
        name="Programmation Python",
        code="PROG-PY",
        description="Introduction à la programmation avec Python",
        subject_type="course",
        credits=6,
        hours_per_week=4,
        department=dept_info
    )
    
    Subject.objects.create(
        name="Base de Données",
        code="BDD",
        description="Conception et gestion de bases de données",
        subject_type="course",
        credits=6, 
        hours_per_week=4,
        department=dept_info
    )
    
    Subject.objects.create(
        name="TP Python",
        code="TP-PY",
        description="Travaux pratiques Python",
        subject_type="practical",
        credits=3,
        hours_per_week=2,
        department=dept_info
    )
    
    print("✅ Matières créées")
    
    # 6. Créer des utilisateurs de test
    # Admin
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@university.edu',
        password='admin123',
        first_name='Super',
        last_name='Admin',
        is_staff=True,
        is_superuser=True
    )
    admin_user.role = 'admin'
    admin_user.save()
    
    # Enseignant
    teacher_user = User.objects.create_user(
        username='prof.martin',
        email='martin@university.edu', 
        password='prof123',
        first_name='Jean',
        last_name='Martin'
    )
    teacher_user.role = 'teacher'
    teacher_user.save()
    
    teacher = Teacher.objects.create(
        user=teacher_user,
        employee_id="EMP001",
        teacher_type="permanent",
        specialization="Informatique",
        phone="+212 6 12 34 56 78",
        max_hours_per_week=20,
        max_hours_per_day=6
    )
    
    # Étudiant
    student_user = User.objects.create_user(
        username='ahmed.benali',
        email='ahmed.benali@etu.university.edu',
        password='student123', 
        first_name='Ahmed',
        last_name='Benali'
    )
    student_user.role = 'student'
    student_user.save()
    
    Student.objects.create(
        user=student_user,
        student_id="ETU2024001",
        program=prog_l3_info,
        enrollment_year=2024
    )
    
    print("✅ Utilisateurs de test créés")
    
    print("\n🎉 Données de test créées avec succès!")
    print("\n📝 Comptes de test créés:")
    print("👨‍💼 Admin: admin / admin123")
    print("👨‍🏫 Enseignant: prof.martin / prof123") 
    print("👨‍🎓 Étudiant: ahmed.benali / student123")

if __name__ == "__main__":
    create_test_data()
