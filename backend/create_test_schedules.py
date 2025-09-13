#!/usr/bin/env python
"""
Script de création de données de test pour les emplois du temps
Exécuter depuis le dossier backend avec: python create_test_schedules.py
"""

import os
import sys
import django
from datetime import datetime, date, time, timedelta

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Department, Program, Room, Subject, Teacher
from schedule.models import Schedule

User = get_user_model()

def create_test_schedules():
    """Créer des emplois du temps de test pour la semaine courante"""
    
    print("🕐 Création d'emplois du temps de test...")
    
    # Obtenir la semaine courante (lundi à dimanche)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    print(f"📅 Semaine du {monday} au {sunday}")
    
    # Vérifier qu'on a les données de base
    try:
        # Récupérer quelques éléments de base
        departments = Department.objects.all()[:3]
        programs = Program.objects.all()[:5]
        rooms = Room.objects.all()[:10]
        subjects = Subject.objects.all()[:8]
        teachers = Teacher.objects.all()[:6]
        
        if not all([departments, programs, rooms, subjects, teachers]):
            print("❌ Données de base manquantes ! Créons d'abord les éléments de base...")
            create_basic_data()
            
            # Récupérer à nouveau
            departments = Department.objects.all()[:3]
            programs = Program.objects.all()[:5]
            rooms = Room.objects.all()[:10]
            subjects = Subject.objects.all()[:8]
            teachers = Teacher.objects.all()[:6]
        
        print(f"✅ Données disponibles:")
        print(f"   - {len(departments)} départements")
        print(f"   - {len(programs)} programmes")
        print(f"   - {len(rooms)} salles")
        print(f"   - {len(subjects)} matières")
        print(f"   - {len(teachers)} enseignants")
        
        # Supprimer les emplois du temps existants pour cette semaine
        Schedule.objects.filter(week_start=monday, week_end=sunday).delete()
        print("🗑️  Emplois du temps existants supprimés")
        
        # Créneaux horaires de base
        time_slots = [
            (time(8, 0), time(9, 30)),    # 8h00 - 9h30
            (time(9, 45), time(11, 15)),  # 9h45 - 11h15
            (time(11, 30), time(13, 0)),  # 11h30 - 13h00
            (time(14, 0), time(15, 30)),  # 14h00 - 15h30
            (time(15, 45), time(17, 15)), # 15h45 - 17h15
        ]
        
        schedules_created = 0
        
        # Créer des emplois du temps pour chaque jour de la semaine (Lundi à Vendredi)
        for day_index in range(5):  # 0=Lundi, 1=Mardi, ..., 4=Vendredi
            day_name = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'][day_index]
            print(f"\n📚 Création d'emplois du temps pour {day_name}...")
            
            # 2-4 cours par jour
            num_courses = min(len(time_slots), 3 + (day_index % 2))
            
            for i in range(num_courses):
                start_time, end_time = time_slots[i]
                
                # Choisir des éléments aléatoirement mais de façon cohérente
                subject = subjects[i % len(subjects)]
                teacher = teachers[i % len(teachers)]
                room = rooms[i % len(rooms)]
                program = programs[i % len(programs)]
                
                # Créer le titre du cours
                title = f"{subject.name} - {program.name}"
                
                # Créer l'emploi du temps
                schedule = Schedule.objects.create(
                    title=title,
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    program=program,
                    day_of_week=day_index,
                    start_time=start_time,
                    end_time=end_time,
                    week_start=monday,
                    week_end=sunday,
                    is_active=True,
                    notes=f"Cours de {subject.name} pour le programme {program.name}"
                )
                
                schedules_created += 1
                print(f"   ✅ {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}: {title}")
        
        print(f"\n🎉 {schedules_created} emplois du temps créés avec succès !")
        print(f"📊 Récapitulatif:")
        print(f"   - Semaine: {monday} au {sunday}")
        print(f"   - Jours avec cours: Lundi à Vendredi")
        print(f"   - Total séances: {schedules_created}")
        print(f"   - Durée moyenne: 1h30 par cours")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des emplois du temps: {e}")
        return False

def create_basic_data():
    """Créer des données de base si elles n'existent pas"""
    
    print("🔧 Création des données de base...")
    
    # Créer un département de test
    dept, created = Department.objects.get_or_create(
        name="Informatique",
        defaults={
            'code': 'INFO',
            'description': 'Département d\'informatique'
        }
    )
    if created:
        print(f"   ✅ Département créé: {dept.name}")
    
    # Créer des programmes de test
    programs_data = [
        ('Licence 1 Informatique', 'L1-INFO', 'license', '1'),
        ('Licence 2 Informatique', 'L2-INFO', 'license', '2'),
        ('Master 1 Informatique', 'M1-INFO', 'master', '1'),
    ]
    
    for name, code, level, year in programs_data:
        program, created = Program.objects.get_or_create(
            name=name,
            defaults={
                'code': code,
                'department': dept,
                'level': level,
                'year': year,
                'duration_semesters': 2
            }
        )
        if created:
            print(f"   ✅ Programme créé: {program.name}")
    
    # Créer des salles de test
    rooms_data = [
        ('Amphi A', 'amphitheater', 150),
        ('Salle TD-01', 'classroom', 30),
        ('Salle TD-02', 'classroom', 35),
        ('Lab Info-01', 'laboratory', 25),
        ('Lab Info-02', 'laboratory', 25),
    ]
    
    for name, room_type, capacity in rooms_data:
        room, created = Room.objects.get_or_create(
            name=name,
            defaults={
                'room_type': room_type,
                'capacity': capacity,
                'floor': 1,
                'building': 'Bâtiment Principal'
            }
        )
        if created:
            print(f"   ✅ Salle créée: {room.name}")
    
    # Créer des matières de test
    subjects_data = [
        ('Algorithmes et Structures de Données', 'ALGO', 'course'),
        ('Programmation Python', 'PYTHON', 'course'),
        ('Base de Données', 'BDD', 'course'),
        ('Développement Web', 'WEB', 'course'),
        ('Mathématiques', 'MATH', 'course'),
        ('Anglais', 'ANG', 'language'),
    ]
    
    for name, code, subject_type in subjects_data:
        subject, created = Subject.objects.get_or_create(
            name=name,
            defaults={
                'code': code,
                'subject_type': subject_type,
                'credits': 3,
                'hours_per_week': 3,
                'department': dept
            }
        )
        if created:
            print(f"   ✅ Matière créée: {subject.name}")
    
    # Créer des enseignants de test
    teachers_data = [
        ('Dr. Ahmed', 'Benali', 'ahmed.benali@university.ma'),
        ('Prof. Fatima', 'Alami', 'fatima.alami@university.ma'),
        ('Dr. Omar', 'Hassani', 'omar.hassani@university.ma'),
    ]
    
    for first_name, last_name, email in teachers_data:
        # Créer l'utilisateur enseignant
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
                'role': 'teacher',
                'is_active': True
            }
        )
        if created:
            user.set_password('teacher123')
            user.save()
            print(f"   ✅ Utilisateur enseignant créé: {user.get_full_name()}")
        
        # Créer le profil enseignant
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': f'T{user.id:04d}',
                'department': dept,
                'specialization': 'Informatique'
            }
        )
        if created:
            print(f"   ✅ Enseignant créé: {teacher.user.get_full_name()}")
    
    print("✅ Données de base créées avec succès !")

if __name__ == '__main__':
    print("🚀 Script de création d'emplois du temps de test")
    print("=" * 50)
    
    success = create_test_schedules()
    
    if success:
        print("\n🎯 SUCCÈS ! Vous pouvez maintenant:")
        print("   1. Actualiser votre page web")
        print("   2. Naviguer vers l'emploi du temps")
        print("   3. Voir les cours créés pour cette semaine")
        print("\n💡 Les emplois du temps sont visibles pour tous les rôles")
    else:
        print("\n❌ ÉCHEC. Vérifiez les erreurs ci-dessus.")
