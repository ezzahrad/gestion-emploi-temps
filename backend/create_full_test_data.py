#!/usr/bin/env python
"""
Script de création de données de test complètes pour AppGET
Exécuter depuis le dossier backend avec: python create_full_test_data.py
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
from core.models import Department, Program, Room, Subject, Teacher, Student
from schedule.models import Schedule

User = get_user_model()

def create_full_test_data():
    """Créer toutes les données de test nécessaires"""
    
    print("🚀 CRÉATION COMPLÈTE DES DONNÉES DE TEST APPGET")
    print("=" * 60)
    
    # 1. CRÉER DÉPARTEMENT
    print("\n📁 Création du département...")
    dept, created = Department.objects.get_or_create(
        name="Informatique",
        defaults={
            'code': 'INFO',
            'description': 'Département d\'informatique et technologies'
        }
    )
    if created:
        print(f"   ✅ Département créé: {dept.name}")
    else:
        print(f"   ℹ️  Département existant: {dept.name}")
    
    # 2. CRÉER PROGRAMMES
    print("\n📚 Création des programmes...")
    programs_data = [
        ('Licence 1 Informatique', 'L1-INFO', 'L1'),
        ('Licence 2 Informatique', 'L2-INFO', 'L2'),
        ('Licence 3 Informatique', 'L3-INFO', 'L3'),
        ('Master 1 Informatique', 'M1-INFO', 'M1'),
        ('Master 2 Informatique', 'M2-INFO', 'M2'),
    ]
    
    programs = []
    for name, code, level in programs_data:
        program, created = Program.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'department': dept,
                'level': level,
                'capacity': 30
            }
        )
        programs.append(program)
        if created:
            print(f"   ✅ Programme créé: {program.name}")
        else:
            print(f"   ℹ️  Programme existant: {program.name}")
    
    # 3. CRÉER SALLES
    print("\n🏢 Création des salles...")
    rooms_data = [
        ('Amphi A', 'AMP-A', 'amphitheater', 150),
        ('Amphi B', 'AMP-B', 'amphitheater', 120),
        ('Salle TD-01', 'TD-01', 'td', 30),
        ('Salle TD-02', 'TD-02', 'td', 35),
        ('Salle TD-03', 'TD-03', 'td', 28),
        ('Lab Info-01', 'LAB-01', 'lab', 25),
        ('Lab Info-02', 'LAB-02', 'lab', 25),
        ('Salle Cours-01', 'C-01', 'lecture', 40),
        ('Salle Cours-02', 'C-02', 'lecture', 45),
        ('Salle Cours-03', 'C-03', 'lecture', 38),
    ]
    
    rooms = []
    for name, code, room_type, capacity in rooms_data:
        room, created = Room.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'room_type': room_type,
                'capacity': capacity,
                'department': dept,
                'equipment': 'Projecteur, Tableau, WiFi' if room_type != 'lab' else 'Projecteur, Ordinateurs, WiFi',
                'is_available': True
            }
        )
        rooms.append(room)
        if created:
            print(f"   ✅ Salle créée: {room.name} ({room.get_room_type_display()})")
        else:
            print(f"   ℹ️  Salle existante: {room.name}")
    
    # 4. CRÉER MATIÈRES
    print("\n📖 Création des matières...")
    subjects_data = [
        ('Algorithmes et Structures de Données', 'ALGO', 'lecture', 6, 6, 1),
        ('Programmation Python', 'PYTHON', 'lab', 4, 4, 1),
        ('Base de Données', 'BDD', 'lecture', 5, 5, 1),
        ('Développement Web', 'WEB', 'lab', 4, 4, 2),
        ('Mathématiques pour l\'Informatique', 'MATH', 'lecture', 6, 6, 1),
        ('Anglais Technique', 'ANG', 'td', 3, 3, 1),
        ('Réseaux Informatiques', 'RESEAU', 'lecture', 5, 5, 2),
        ('Intelligence Artificielle', 'IA', 'lecture', 6, 6, 2),
        ('Génie Logiciel', 'GL', 'lecture', 5, 5, 2),
        ('Systèmes d\'Exploitation', 'OS', 'lecture', 5, 5, 1),
    ]
    
    subjects = []
    for name, code, subject_type, credits, hours, semester in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'department': dept,
                'subject_type': subject_type,
                'credits': credits,
                'hours_per_week': hours,
                'semester': semester,
                'description': f'Cours de {name}'
            }
        )
        subjects.append(subject)
        if created:
            print(f"   ✅ Matière créée: {subject.name} ({subject.get_subject_type_display()})")
            # Associer aux programmes
            subject.program.set(programs[:3])  # L1, L2, L3
        else:
            print(f"   ℹ️  Matière existante: {subject.name}")
    
    # 5. CRÉER ENSEIGNANTS
    print("\n👨‍🏫 Création des enseignants...")
    teachers_data = [
        ('Ahmed', 'Benali', 'ahmed.benali@university.ma', 'Algorithmes et Programmation'),
        ('Fatima', 'Alami', 'fatima.alami@university.ma', 'Base de Données et Systèmes'),
        ('Omar', 'Hassani', 'omar.hassani@university.ma', 'Réseaux et Sécurité'),
        ('Aicha', 'Tazi', 'aicha.tazi@university.ma', 'Intelligence Artificielle'),
        ('Youssef', 'Mansouri', 'youssef.mansouri@university.ma', 'Génie Logiciel'),
        ('Khadija', 'Berrada', 'khadija.berrada@university.ma', 'Mathématiques'),
    ]
    
    teachers = []
    for first_name, last_name, email, specialization in teachers_data:
        # Créer l'utilisateur enseignant
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
                'role': 'teacher',
                'department': dept,
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
                'specialization': specialization,
                'max_hours_per_week': 20,
                'is_available': True
            }
        )
        teachers.append(teacher)
        
        if created:
            # Associer quelques matières à l'enseignant
            teacher.subjects.set(subjects[:3])  # Premières 3 matières
            print(f"   ✅ Enseignant créé: {teacher.user.get_full_name()}")
        else:
            print(f"   ℹ️  Enseignant existant: {teacher.user.get_full_name()}")
    
    # 6. CRÉER QUELQUES ÉTUDIANTS
    print("\n👨‍🎓 Création des étudiants...")
    students_data = [
        ('Mohammed', 'Alaoui', 'mohammed.alaoui@etu.university.ma', 0),  # L1
        ('Sara', 'Benjelloun', 'sara.benjelloun@etu.university.ma', 1),  # L2
        ('Hamza', 'Idrissi', 'hamza.idrissi@etu.university.ma', 2),      # L3
    ]
    
    for first_name, last_name, email, program_index in students_data:
        # Créer l'utilisateur étudiant
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
                'role': 'student',
                'program': programs[program_index],
                'is_active': True
            }
        )
        if created:
            user.set_password('etudiant123')
            user.save()
            print(f"   ✅ Utilisateur étudiant créé: {user.get_full_name()}")
        
        # Créer le profil étudiant
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'student_id': f'S{user.id:06d}',
                'program': programs[program_index],
                'enrollment_year': 2024,
                'is_active': True
            }
        )
        if created:
            print(f"   ✅ Étudiant créé: {student.user.get_full_name()} - {student.program.name}")
        else:
            print(f"   ℹ️  Étudiant existant: {student.user.get_full_name()}")
    
    # 7. CRÉER EMPLOIS DU TEMPS POUR LA SEMAINE COURANTE
    print("\n📅 Création des emplois du temps...")
    
    # Obtenir la semaine courante (lundi à dimanche)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    print(f"   📅 Semaine du {monday} au {sunday}")
    
    # Supprimer les emplois du temps existants pour cette semaine
    deleted_count = Schedule.objects.filter(week_start=monday, week_end=sunday).count()
    Schedule.objects.filter(week_start=monday, week_end=sunday).delete()
    if deleted_count > 0:
        print(f"   🗑️  {deleted_count} emplois du temps existants supprimés")
    
    # Créneaux horaires
    time_slots = [
        (time(8, 0), time(9, 30)),    # 8h00 - 9h30
        (time(9, 45), time(11, 15)),  # 9h45 - 11h15
        (time(11, 30), time(13, 0)),  # 11h30 - 13h00
        (time(14, 0), time(15, 30)),  # 14h00 - 15h30
        (time(15, 45), time(17, 15)), # 15h45 - 17h15
    ]
    
    schedules_created = 0
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    
    # Créer des emplois du temps pour chaque jour (Lundi à Vendredi)
    for day_index in range(5):  # 0=Lundi, 1=Mardi, ..., 4=Vendredi
        day_name = day_names[day_index]
        print(f"\n   📚 {day_name}:")
        
        # 3-4 cours par jour
        num_courses = 3 + (day_index % 2)
        
        for i in range(min(num_courses, len(time_slots))):
            start_time, end_time = time_slots[i]
            
            # Rotation des éléments pour varier
            subject = subjects[i % len(subjects)]
            teacher = teachers[i % len(teachers)]
            room = rooms[(i + day_index) % len(rooms)]
            program = programs[i % min(3, len(programs))]  # Seulement L1, L2, L3
            
            # Créer le titre du cours
            title = f"{subject.name} - {program.name}"
            
            try:
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
                    notes=f"Cours de {subject.name} en {room.name}"
                )
                
                schedules_created += 1
                print(f"      ✅ {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}: {title}")
                
            except Exception as e:
                print(f"      ❌ Erreur pour {title}: {e}")
    
    # 8. RÉSUMÉ FINAL
    print(f"\n🎉 CRÉATION TERMINÉE AVEC SUCCÈS !")
    print("=" * 50)
    print(f"📊 Données créées:")
    print(f"   📁 Départements: {Department.objects.count()}")
    print(f"   📚 Programmes: {Program.objects.count()}")
    print(f"   🏢 Salles: {Room.objects.count()}")
    print(f"   📖 Matières: {Subject.objects.count()}")
    print(f"   👨‍🏫 Enseignants: {Teacher.objects.count()}")
    print(f"   👨‍🎓 Étudiants: {Student.objects.count()}")
    print(f"   📅 Emplois du temps (cette semaine): {schedules_created}")
    print(f"   👥 Utilisateurs totaux: {User.objects.count()}")
    
    print(f"\n🔑 Comptes de test créés:")
    print(f"   👑 Admin: admin@university.ma / admin123")
    print(f"   👨‍🏫 Enseignant: ahmed.benali@university.ma / teacher123")
    print(f"   👨‍🎓 Étudiant: mohammed.alaoui@etu.university.ma / etudiant123")
    
    print(f"\n🚀 VOTRE APPLICATION EST PRÊTE !")
    print(f"   1. Frontend: http://localhost:3000")
    print(f"   2. Backend: http://localhost:8000")
    print(f"   3. Admin Django: http://localhost:8000/admin")
    
    return True

if __name__ == '__main__':
    try:
        success = create_full_test_data()
        if success:
            print(f"\n✅ SUCCESS! Votre base de données contient maintenant toutes les données nécessaires.")
            print(f"💡 Actualisez votre page web pour voir les données !")
        else:
            print(f"\n❌ ÉCHEC - Vérifiez les erreurs ci-dessus")
    except Exception as e:
        print(f"\n💥 ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
