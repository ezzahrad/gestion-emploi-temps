# create_sample_database.py - Créer une base de données exemplaire complète
import os
import django
from django.contrib.auth.hashers import make_password
from datetime import date, time, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from authentication.models import User
from core.models import *
from schedule.models import *

def clear_existing_data():
    """Nettoyer les données existantes (optionnel)"""
    print("🗑️  Nettoyage des anciennes données...")
    
    # Garder les utilisateurs admin existants
    admin_users = User.objects.filter(role='admin').values_list('email', flat=True)
    print(f"ℹ️  Conservation de {len(admin_users)} administrateurs existants")
    
    # Supprimer seulement les données de test
    Schedule.objects.all().delete()
    Student.objects.all().delete() 
    Teacher.objects.all().delete()
    Subject.objects.all().delete()
    Room.objects.all().delete()
    Program.objects.all().delete()
    Department.objects.all().delete()
    
    # Supprimer les utilisateurs non-admin
    User.objects.exclude(role='admin').delete()
    
    print("✅ Nettoyage terminé")

def create_departments():
    """Créer les départements"""
    print("🏛️  Création des départements...")
    
    departments_data = [
        {
            'name': 'Informatique et Sciences du Numérique',
            'code': 'ISEN', 
            'description': 'Département spécialisé en informatique, intelligence artificielle et sciences du numérique'
        },
        {
            'name': 'Mathématiques et Statistiques',
            'code': 'MATH',
            'description': 'Département de mathématiques pures et appliquées, statistiques et actuariat'
        },
        {
            'name': 'Physique et Sciences de l\'Ingénieur', 
            'code': 'PHYS',
            'description': 'Département de physique fondamentale et appliquée, génie physique'
        },
        {
            'name': 'Sciences Économiques et de Gestion',
            'code': 'SEGC', 
            'description': 'Département d\'économie, gestion, finance et commerce'
        },
        {
            'name': 'Langues et Communication',
            'code': 'LANG',
            'description': 'Département des langues étrangères et communication'
        }
    ]
    
    departments = []
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        departments.append(dept)
        print(f"✅ {dept.name}")
    
    return departments

def create_programs(departments):
    """Créer les programmes d'études"""
    print("📚 Création des programmes...")
    
    programs_data = [
        # Informatique
        {'name': 'Licence Informatique Fondamentale', 'code': 'LIF', 'level': 'L1', 'dept': 'ISEN', 'capacity': 40},
        {'name': 'Licence Informatique Fondamentale', 'code': 'LIF', 'level': 'L2', 'dept': 'ISEN', 'capacity': 35}, 
        {'name': 'Licence Informatique Fondamentale', 'code': 'LIF', 'level': 'L3', 'dept': 'ISEN', 'capacity': 30},
        {'name': 'Master Intelligence Artificielle', 'code': 'MIA', 'level': 'M1', 'dept': 'ISEN', 'capacity': 25},
        {'name': 'Master Intelligence Artificielle', 'code': 'MIA', 'level': 'M2', 'dept': 'ISEN', 'capacity': 20},
        {'name': 'Master Sécurité Informatique', 'code': 'MSI', 'level': 'M1', 'dept': 'ISEN', 'capacity': 20},
        {'name': 'Master Sécurité Informatique', 'code': 'MSI', 'level': 'M2', 'dept': 'ISEN', 'capacity': 18},
        
        # Mathématiques  
        {'name': 'Licence Mathématiques', 'code': 'LMA', 'level': 'L1', 'dept': 'MATH', 'capacity': 35},
        {'name': 'Licence Mathématiques', 'code': 'LMA', 'level': 'L2', 'dept': 'MATH', 'capacity': 30},
        {'name': 'Licence Mathématiques', 'code': 'LMA', 'level': 'L3', 'dept': 'MATH', 'capacity': 25},
        {'name': 'Master Mathématiques Appliquées', 'code': 'MMA', 'level': 'M1', 'dept': 'MATH', 'capacity': 20},
        {'name': 'Master Mathématiques Appliquées', 'code': 'MMA', 'level': 'M2', 'dept': 'MATH', 'capacity': 18},
        
        # Physique
        {'name': 'Licence Physique', 'code': 'LPH', 'level': 'L1', 'dept': 'PHYS', 'capacity': 30},
        {'name': 'Licence Physique', 'code': 'LPH', 'level': 'L2', 'dept': 'PHYS', 'capacity': 25},
        {'name': 'Licence Physique', 'code': 'LPH', 'level': 'L3', 'dept': 'PHYS', 'capacity': 20},
        
        # Économie
        {'name': 'Licence Sciences Économiques', 'code': 'LSE', 'level': 'L1', 'dept': 'SEGC', 'capacity': 45},
        {'name': 'Licence Sciences Économiques', 'code': 'LSE', 'level': 'L2', 'dept': 'SEGC', 'capacity': 40},
        {'name': 'Licence Sciences Économiques', 'code': 'LSE', 'level': 'L3', 'dept': 'SEGC', 'capacity': 35},
        {'name': 'Master Finance et Banque', 'code': 'MFB', 'level': 'M1', 'dept': 'SEGC', 'capacity': 25},
        {'name': 'Master Finance et Banque', 'code': 'MFB', 'level': 'M2', 'dept': 'SEGC', 'capacity': 22}
    ]
    
    programs = []
    dept_dict = {dept.code: dept for dept in departments}
    
    for prog_data in programs_data:
        department = dept_dict[prog_data['dept']]
        
        prog, created = Program.objects.get_or_create(
            code=f"{prog_data['code']}-{prog_data['level']}",
            defaults={
                'name': f"{prog_data['name']} - {prog_data['level']}",
                'department': department,
                'level': prog_data['level'],
                'capacity': prog_data['capacity']
            }
        )
        programs.append(prog)
        print(f"✅ {prog.name}")
    
    return programs

def create_rooms(departments):
    """Créer les salles"""
    print("🏢 Création des salles...")
    
    rooms_data = []
    
    # Salles par département
    for dept in departments:
        dept_code = dept.code
        
        # Amphithéâtres
        rooms_data.extend([
            {'name': f'Amphithéâtre {dept_code}-A1', 'code': f'AMPH-{dept_code}-A1', 'type': 'amphitheater', 'capacity': 200, 'dept': dept},
            {'name': f'Amphithéâtre {dept_code}-A2', 'code': f'AMPH-{dept_code}-A2', 'type': 'amphitheater', 'capacity': 150, 'dept': dept},
        ])
        
        # Salles de cours
        for i in range(1, 6):
            rooms_data.append({
                'name': f'Salle de cours {dept_code}-{i:02d}',
                'code': f'COURS-{dept_code}-{i:02d}',
                'type': 'classroom',
                'capacity': random.randint(30, 50),
                'dept': dept
            })
        
        # Salles de TD
        for i in range(1, 4):
            rooms_data.append({
                'name': f'Salle TD {dept_code}-{i:02d}',
                'code': f'TD-{dept_code}-{i:02d}',
                'type': 'classroom', 
                'capacity': random.randint(25, 35),
                'dept': dept
            })
        
        # Laboratoires (surtout pour ISEN et PHYS)
        if dept_code in ['ISEN', 'PHYS']:
            for i in range(1, 4):
                rooms_data.append({
                    'name': f'Laboratoire {dept_code}-{i:02d}',
                    'code': f'LAB-{dept_code}-{i:02d}',
                    'type': 'laboratory',
                    'capacity': random.randint(20, 30),
                    'dept': dept
                })
    
    rooms = []
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            code=room_data['code'],
            defaults={
                'name': room_data['name'],
                'room_type': room_data['type'],
                'capacity': room_data['capacity'],
                'building': f"Bâtiment {room_data['dept'].code}",
                'floor': random.choice(['RDC', '1er étage', '2ème étage']),
                'equipment': 'Projecteur, Tableau, WiFi',
                'department': room_data['dept']
            }
        )
        rooms.append(room)
    
    print(f"✅ {len(rooms)} salles créées")
    return rooms

def create_admin_users():
    """Créer les utilisateurs administrateurs"""
    print("👑 Création des administrateurs...")
    
    admins_data = [
        {'first_name': 'Hassan', 'last_name': 'BENALI', 'email': 'hassan.benali@university.ma', 'username': 'h.benali'},
        {'first_name': 'Fatima', 'last_name': 'ALAOUI', 'email': 'fatima.alaoui@university.ma', 'username': 'f.alaoui'},
        {'first_name': 'Mohamed', 'last_name': 'TAZI', 'email': 'mohamed.tazi@university.ma', 'username': 'm.tazi'},
    ]
    
    admins = []
    for admin_data in admins_data:
        user, created = User.objects.get_or_create(
            email=admin_data['email'],
            defaults={
                'username': admin_data['username'],
                'first_name': admin_data['first_name'],
                'last_name': admin_data['last_name'],
                'password': make_password('admin2024'),
                'role': 'admin',
                'is_staff': True,
                'is_active': True
            }
        )
        admins.append(user)
        print(f"✅ {user.first_name} {user.last_name} - {user.email}")
    
    return admins

def create_department_heads(departments):
    """Créer les chefs de département"""
    print("🏛️  Création des chefs de département...")
    
    heads_data = [
        {'dept': 'ISEN', 'first_name': 'Karim', 'last_name': 'MANSOURI', 'email': 'karim.mansouri@university.ma'},
        {'dept': 'MATH', 'first_name': 'Aicha', 'last_name': 'BENHADOU', 'email': 'aicha.benhadou@university.ma'},
        {'dept': 'PHYS', 'first_name': 'Omar', 'last_name': 'LAKHAL', 'email': 'omar.lakhal@university.ma'},
        {'dept': 'SEGC', 'first_name': 'Nadia', 'last_name': 'CHAKIR', 'email': 'nadia.chakir@university.ma'},
        {'dept': 'LANG', 'first_name': 'Rachid', 'last_name': 'ZOUANI', 'email': 'rachid.zouani@university.ma'},
    ]
    
    dept_dict = {dept.code: dept for dept in departments}
    heads = []
    
    for head_data in heads_data:
        department = dept_dict[head_data['dept']]
        username = f"{head_data['first_name'].lower()}.{head_data['last_name'].lower()}"
        
        user, created = User.objects.get_or_create(
            email=head_data['email'],
            defaults={
                'username': username,
                'first_name': head_data['first_name'],
                'last_name': head_data['last_name'],
                'password': make_password('chef2024'),
                'role': 'department_head',
                'is_active': True
            }
        )
        
        # Assigner comme chef de département
        department.head = user
        department.save()
        
        heads.append(user)
        print(f"✅ {user.first_name} {user.last_name} - Chef {department.name}")
    
    return heads

def create_teachers(departments):
    """Créer les enseignants"""
    print("👨‍🏫 Création des enseignants...")
    
    # Prénoms et noms marocains
    first_names_m = ['Ahmed', 'Mohamed', 'Hassan', 'Omar', 'Youssef', 'Khalid', 'Abderrahim', 'Mustapha', 'Brahim', 'Samir']
    first_names_f = ['Fatima', 'Aicha', 'Khadija', 'Zineb', 'Nadia', 'Samira', 'Salma', 'Hafida', 'Latifa', 'Meriem']
    last_names = ['ALAOUI', 'BENALI', 'TAZI', 'MANSOURI', 'CHAKIR', 'LAKHAL', 'ZOUANI', 'BENHADOU', 'FASSI', 'IDRISSI', 'BENNANI', 'CHERKAOUI']
    
    specializations = {
        'ISEN': ['Informatique Théorique', 'Programmation', 'Base de Données', 'Intelligence Artificielle', 'Sécurité Informatique', 'Réseaux', 'Génie Logiciel'],
        'MATH': ['Algèbre', 'Analyse', 'Probabilités', 'Statistiques', 'Mathématiques Appliquées', 'Géométrie'],
        'PHYS': ['Physique Théorique', 'Électronique', 'Optique', 'Mécanique Quantique', 'Thermodynamique'],
        'SEGC': ['Microéconomie', 'Macroéconomie', 'Finance', 'Gestion', 'Marketing', 'Comptabilité'],
        'LANG': ['Anglais', 'Français', 'Espagnol', 'Communication', 'Littérature']
    }
    
    teachers = []
    
    for department in departments:
        # 8-12 enseignants par département
        num_teachers = random.randint(8, 12)
        
        for i in range(num_teachers):
            # Choisir prénom selon le genre (random)
            is_male = random.choice([True, False])
            first_name = random.choice(first_names_m if is_male else first_names_f)
            last_name = random.choice(last_names)
            
            # Email et username
            username = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{username}@university.ma"
            
            # Vérifier unicité
            counter = 1
            original_username = username
            original_email = email
            
            while User.objects.filter(email=email).exists():
                username = f"{original_username}{counter}"
                email = f"{original_username}{counter}@university.ma"
                counter += 1
            
            # Créer utilisateur
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password('prof2024'),
                role='teacher',
                is_active=True
            )
            
            # Créer profil enseignant
            teacher = Teacher.objects.create(
                user=user,
                employee_id=f"EMP{department.code}{i+1:03d}",
                teacher_type=random.choice(['permanent', 'contractual', 'guest']),
                specialization=random.choice(specializations[department.code]),
                department=department,
                phone=f"+212 6{random.randint(10000000, 99999999)}",
                max_hours_per_week=random.randint(16, 24),
                max_hours_per_day=random.randint(6, 8)
            )
            
            teachers.append(teacher)
            print(f"✅ {user.first_name} {user.last_name} - {teacher.specialization} ({department.code})")
    
    return teachers

def create_students(programs):
    """Créer les étudiants"""
    print("👨‍🎓 Création des étudiants...")
    
    # Prénoms et noms pour étudiants
    first_names_m = ['Youssef', 'Amine', 'Hamza', 'Adam', 'Taha', 'Imran', 'Zakaria', 'Othmane', 'Mehdi', 'Anas', 'Ismail', 'Hicham']
    first_names_f = ['Fatima', 'Zineb', 'Salma', 'Imane', 'Meryem', 'Nour', 'Aya', 'Kenza', 'Dounia', 'Jihane', 'Amina', 'Chaimaa']
    last_names = ['ALAMI', 'BERRADA', 'CHRAIBI', 'DRISSI', 'ELOUAFI', 'FASSI', 'GUENNOUN', 'HAJJI', 'IDRISSI', 'JABRI', 'KETTANI', 'LAHLOU']
    
    students = []
    current_year = date.today().year
    
    for program in programs:
        # Nombre d'étudiants selon la capacité du programme
        num_students = random.randint(int(program.capacity * 0.7), program.capacity)
        
        for i in range(num_students):
            # Choisir prénom selon le genre
            is_male = random.choice([True, False])
            first_name = random.choice(first_names_m if is_male else first_names_f)
            last_name = random.choice(last_names)
            
            # ID étudiant unique
            level_num = {'L1': 1, 'L2': 2, 'L3': 3, 'M1': 4, 'M2': 5}[program.level]
            student_id = f"{current_year}{program.department.code}{level_num}{i+1:03d}"
            
            # Email étudiant
            username = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{username}.etu{i+1:03d}@university.ma"
            
            # Vérifier unicité email
            counter = 1
            original_email = email
            while User.objects.filter(email=email).exists():
                email = f"{username}.etu{i+counter:03d}@university.ma"
                counter += 1
            
            # Année d'inscription selon le niveau
            enrollment_year = current_year - (level_num - 1)
            
            # Créer utilisateur
            user = User.objects.create(
                username=email.split('@')[0],
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password('etudiant2024'),
                role='student',
                is_active=True
            )
            
            # Créer profil étudiant
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                program=program,
                enrollment_year=enrollment_year,
                phone=f"+212 6{random.randint(10000000, 99999999)}"
            )
            
            students.append(student)
        
        print(f"✅ {num_students} étudiants créés pour {program.name}")
    
    return students

def create_subjects(departments, programs):
    """Créer les matières"""
    print("📖 Création des matières...")
    
    subjects_by_dept = {
        'ISEN': [
            ('Algorithmique et Programmation', 'ALGO', 6, 4, 'course'),
            ('Base de Données', 'BDD', 6, 4, 'course'),
            ('Systèmes d\'Exploitation', 'SE', 4, 3, 'course'),
            ('Réseaux Informatiques', 'NET', 4, 3, 'course'),
            ('Intelligence Artificielle', 'IA', 6, 4, 'course'),
            ('Sécurité Informatique', 'SEC', 4, 3, 'course'),
            ('Génie Logiciel', 'GL', 6, 4, 'course'),
            ('TP Programmation', 'TP-PROG', 3, 2, 'practical'),
            ('TP Base de Données', 'TP-BDD', 3, 2, 'practical'),
            ('Projet Informatique', 'PROJ-INFO', 8, 6, 'project'),
        ],
        'MATH': [
            ('Algèbre Linéaire', 'ALG', 6, 4, 'course'),
            ('Analyse Mathématique', 'ANA', 6, 4, 'course'),
            ('Probabilités et Statistiques', 'PROB', 6, 4, 'course'),
            ('Mathématiques Appliquées', 'MAPP', 4, 3, 'course'),
            ('Géométrie', 'GEO', 4, 3, 'course'),
            ('TD Algèbre', 'TD-ALG', 3, 2, 'practical'),
            ('TD Analyse', 'TD-ANA', 3, 2, 'practical'),
        ],
        'PHYS': [
            ('Mécanique Classique', 'MEC', 6, 4, 'course'),
            ('Électromagnétisme', 'ELEC', 6, 4, 'course'),
            ('Thermodynamique', 'THERMO', 4, 3, 'course'),
            ('Optique', 'OPT', 4, 3, 'course'),
            ('TP Physique', 'TP-PHYS', 4, 3, 'practical'),
        ],
        'SEGC': [
            ('Microéconomie', 'MICRO', 6, 4, 'course'),
            ('Macroéconomie', 'MACRO', 6, 4, 'course'),
            ('Gestion Financière', 'GF', 4, 3, 'course'),
            ('Marketing', 'MKT', 4, 3, 'course'),
            ('Comptabilité', 'COMPTA', 4, 3, 'course'),
            ('TD Économie', 'TD-ECO', 2, 2, 'practical'),
        ],
        'LANG': [
            ('Anglais', 'ANG', 3, 2, 'course'),
            ('Français', 'FR', 3, 2, 'course'),
            ('Communication', 'COM', 2, 2, 'course'),
        ]
    }
    
    subjects = []
    
    for department in departments:
        dept_subjects = subjects_by_dept.get(department.code, [])
        
        for subj_data in dept_subjects:
            name, code, credits, hours, subj_type = subj_data
            
            subject, created = Subject.objects.get_or_create(
                code=f"{department.code}-{code}",
                defaults={
                    'name': name,
                    'description': f"Cours de {name} - {department.name}",
                    'subject_type': subj_type,
                    'credits': credits,
                    'hours_per_week': hours,
                    'department': department
                }
            )
            subjects.append(subject)
            print(f"✅ {subject.name} ({subject.code})")
    
    return subjects

def create_sample_schedules(programs, subjects, teachers, rooms):
    """Créer quelques emplois du temps d'exemple"""
    print("📅 Création d'emplois du temps d'exemple...")
    
    # Créer quelques créneaux horaires
    time_slots = [
        {'day': 0, 'start': '08:00', 'end': '09:30'},  # Lundi 8h-9h30
        {'day': 0, 'start': '10:00', 'end': '11:30'},  # Lundi 10h-11h30
        {'day': 0, 'start': '14:00', 'end': '15:30'},  # Lundi 14h-15h30
        {'day': 1, 'start': '08:00', 'end': '09:30'},  # Mardi 8h-9h30
        {'day': 1, 'start': '10:00', 'end': '11:30'},  # Mardi 10h-11h30
        {'day': 2, 'start': '08:00', 'end': '09:30'},  # Mercredi 8h-9h30
        {'day': 3, 'start': '14:00', 'end': '15:30'},  # Jeudi 14h-15h30
        {'day': 4, 'start': '08:00', 'end': '09:30'},  # Vendredi 8h-9h30
    ]
    
    schedules = []
    
    # Créer 20-30 emplois du temps d'exemple
    for i in range(25):
        program = random.choice(programs)
        subject = random.choice([s for s in subjects if s.department == program.department])
        teacher = random.choice([t for t in teachers if t.department == program.department])
        room = random.choice([r for r in rooms if r.department == program.department])
        time_slot = random.choice(time_slots)
        
        # Date de début (semaine prochaine)
        start_date = date.today() + timedelta(days=7)
        
        try:
            schedule = Schedule.objects.create(
                program=program,
                subject=subject,
                teacher=teacher,
                room=room,
                day_of_week=time_slot['day'],
                start_time=time_slot['start'],
                end_time=time_slot['end'],
                start_date=start_date,
                end_date=start_date + timedelta(days=90),  # 3 mois
                status='confirmed'
            )
            schedules.append(schedule)
        except Exception as e:
            print(f"⚠️  Conflit pour {subject.name} - {e}")
    
    print(f"✅ {len(schedules)} emplois du temps créés")
    return schedules

def generate_user_summary():
    """Générer un résumé des utilisateurs créés"""
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DE LA BASE DE DONNÉES CRÉÉE")
    print("="*80)
    
    # Compter les utilisateurs par rôle
    roles_count = {}
    for role, label in [('admin', 'Administrateurs'), ('department_head', 'Chefs de département'), 
                       ('teacher', 'Enseignants'), ('student', 'Étudiants')]:
        count = User.objects.filter(role=role).count()
        roles_count[role] = count
        print(f"👥 {label}: {count}")
    
    print(f"\n🏛️  Départements: {Department.objects.count()}")
    print(f"📚 Programmes: {Program.objects.count()}")
    print(f"🏢 Salles: {Room.objects.count()}")
    print(f"📖 Matières: {Subject.objects.count()}")
    print(f"📅 Emplois du temps: {Schedule.objects.count()}")
    
    # Générer fichier de comptes
    print(f"\n📝 Génération du fichier des comptes utilisateurs...")
    
    accounts_file = "comptes_utilisateurs.txt"
    with open(accounts_file, 'w', encoding='utf-8') as f:
        f.write("🎓 UNIVERSITÉ - COMPTES UTILISATEURS APPGET\n")
        f.write("="*60 + "\n\n")
        
        # Administrateurs
        f.write("👑 ADMINISTRATEURS\n")
        f.write("-"*40 + "\n")
        for admin in User.objects.filter(role='admin'):
            f.write(f"Nom: {admin.first_name} {admin.last_name}\n")
            f.write(f"Email: {admin.email}\n")
            f.write(f"Mot de passe: admin2024\n")
            f.write("-"*20 + "\n")
        
        # Chefs de département
        f.write("\n🏛️  CHEFS DE DÉPARTEMENT\n")
        f.write("-"*40 + "\n")
        for head in User.objects.filter(role='department_head'):
            dept = Department.objects.filter(head=head).first()
            f.write(f"Nom: {head.first_name} {head.last_name}\n")
            f.write(f"Email: {head.email}\n")
            f.write(f"Département: {dept.name if dept else 'N/A'}\n")
            f.write(f"Mot de passe: chef2024\n")
            f.write("-"*20 + "\n")
        
        # Quelques enseignants (les 10 premiers)
        f.write("\n👨‍🏫 ENSEIGNANTS (échantillon)\n")
        f.write("-"*40 + "\n")
        for teacher_user in User.objects.filter(role='teacher')[:10]:
            teacher = Teacher.objects.filter(user=teacher_user).first()
            f.write(f"Nom: {teacher_user.first_name} {teacher_user.last_name}\n")
            f.write(f"Email: {teacher_user.email}\n")
            f.write(f"Spécialisation: {teacher.specialization if teacher else 'N/A'}\n")
            f.write(f"Département: {teacher.department.name if teacher else 'N/A'}\n")
            f.write(f"Mot de passe: prof2024\n")
            f.write("-"*20 + "\n")
        
        # Quelques étudiants (les 10 premiers)
        f.write("\n👨‍🎓 ÉTUDIANTS (échantillon)\n")
        f.write("-"*40 + "\n")
        for student_user in User.objects.filter(role='student')[:10]:
            student = Student.objects.filter(user=student_user).first()
            f.write(f"Nom: {student_user.first_name} {student_user.last_name}\n")
            f.write(f"Email: {student_user.email}\n")
            f.write(f"ID Étudiant: {student.student_id if student else 'N/A'}\n")
            f.write(f"Programme: {student.program.name if student else 'N/A'}\n")
            f.write(f"Mot de passe: etudiant2024\n")
            f.write("-"*20 + "\n")
        
        f.write(f"\n📊 STATISTIQUES TOTALES\n")
        f.write("-"*40 + "\n")
        f.write(f"Total utilisateurs: {User.objects.count()}\n")
        f.write(f"Administrateurs: {roles_count['admin']}\n")
        f.write(f"Chefs de département: {roles_count['department_head']}\n")
        f.write(f"Enseignants: {roles_count['teacher']}\n")
        f.write(f"Étudiants: {roles_count['student']}\n")
    
    print(f"✅ Fichier créé: {accounts_file}")

def main():
    """Fonction principale"""
    print("🎓 CRÉATION D'UNE BASE DE DONNÉES EXEMPLAIRE - APPGET")
    print("="*80)
    
    # Demander confirmation pour nettoyer
    response = input("Voulez-vous nettoyer les données existantes (garder les admins)? (y/N): ")
    if response.lower() == 'y':
        clear_existing_data()
    
    print("\n🚀 Début de la création des données...")
    
    # Créer les données de base
    departments = create_departments()
    programs = create_programs(departments) 
    rooms = create_rooms(departments)
    
    # Créer les utilisateurs
    admins = create_admin_users()
    heads = create_department_heads(departments)
    teachers = create_teachers(departments)
    subjects = create_subjects(departments, programs)
    students = create_students(programs)
    
    # Créer quelques emplois du temps
    schedules = create_sample_schedules(programs, subjects, teachers, rooms)
    
    # Générer le résumé
    generate_user_summary()
    
    print("\n🎉 BASE DE DONNÉES EXEMPLAIRE CRÉÉE AVEC SUCCÈS!")
    print(f"📁 Consultez le fichier 'comptes_utilisateurs.txt' pour tous les détails")
    print("\n🚀 Vous pouvez maintenant tester votre application avec des données réalistes!")

if __name__ == "__main__":
    main()
