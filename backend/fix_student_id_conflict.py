# fix_student_id_conflict.py - Corriger rapidement le conflit d'ID étudiants
import os
import django
from django.contrib.auth.hashers import make_password
from datetime import date
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from authentication.models import User
from core.models import *

def fix_and_create_remaining_students():
    """Corriger les conflits d'ID et créer les étudiants restants"""
    print("🔧 Correction du conflit d'ID étudiants...")
    
    # Prénoms et noms pour étudiants
    first_names_m = ['Youssef', 'Amine', 'Hamza', 'Adam', 'Taha', 'Imran', 'Zakaria', 'Othmane', 'Mehdi', 'Anas', 'Ismail', 'Hicham']
    first_names_f = ['Fatima', 'Zineb', 'Salma', 'Imane', 'Meryem', 'Nour', 'Aya', 'Kenza', 'Dounia', 'Jihane', 'Amina', 'Chaimaa']
    last_names = ['ALAMI', 'BERRADA', 'CHRAIBI', 'DRISSI', 'ELOUAFI', 'FASSI', 'GUENNOUN', 'HAJJI', 'IDRISSI', 'JABRI', 'KETTANI', 'LAHLOU']
    
    # Compteur global pour éviter les conflits
    global_student_counter = Student.objects.count() + 1
    
    current_year = date.today().year
    students_created = 0
    
    # Traiter tous les programmes qui n'ont pas encore d'étudiants ou qui en manquent
    programs = Program.objects.all()
    
    for program in programs:
        current_students_count = Student.objects.filter(program=program).count()
        needed_students = max(0, program.capacity - current_students_count)
        
        if needed_students > 0:
            print(f"📚 Ajout de {needed_students} étudiants pour {program.name}")
            
            for i in range(needed_students):
                # Choisir prénom selon le genre
                is_male = random.choice([True, False])
                first_name = random.choice(first_names_m if is_male else first_names_f)
                last_name = random.choice(last_names)
                
                # ID étudiant unique avec compteur global
                student_id = f"{current_year}{program.code.replace('-', '')}{global_student_counter:04d}"
                global_student_counter += 1
                
                # Vérifier unicité (au cas où)
                while Student.objects.filter(student_id=student_id).exists():
                    student_id = f"{current_year}{program.code.replace('-', '')}{global_student_counter:04d}"
                    global_student_counter += 1
                
                # Email étudiant unique
                base_username = f"{first_name.lower()}.{last_name.lower()}"
                email = f"{base_username}.{global_student_counter:04d}@university.ma"
                
                # Vérifier unicité email
                counter = 1
                while User.objects.filter(email=email).exists():
                    email = f"{base_username}.{global_student_counter + counter:04d}@university.ma"
                    counter += 1
                
                # Année d'inscription selon le niveau
                level_num = {'L1': 1, 'L2': 2, 'L3': 3, 'M1': 4, 'M2': 5}[program.level]
                enrollment_year = current_year - (level_num - 1)
                
                try:
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
                        is_active=True
                    )
                    
                    students_created += 1
                    
                except Exception as e:
                    print(f"❌ Erreur création étudiant {first_name} {last_name}: {e}")
                    continue
    
    print(f"✅ {students_created} étudiants créés avec succès")
    
    # Statistiques finales
    total_students = Student.objects.count()
    print(f"📊 Total étudiants en base: {total_students}")
    
    # Par programme
    print("\n📚 Répartition par programme:")
    for program in programs:
        count = Student.objects.filter(program=program).count()
        print(f"   {program.name}: {count}/{program.capacity} étudiants")

def generate_final_summary():
    """Générer le résumé final"""
    print("\n" + "="*80)
    print("🎉 BASE DE DONNÉES FINALEMENT COMPLÈTE!")
    print("="*80)
    
    # Compter tous les utilisateurs
    roles_count = {
        'admin': User.objects.filter(role='admin').count(),
        'department_head': User.objects.filter(role='department_head').count(),
        'teacher': User.objects.filter(role='teacher').count(),
        'student': User.objects.filter(role='student').count()
    }
    
    print("👥 UTILISATEURS:")
    print(f"   👑 Administrateurs: {roles_count['admin']}")
    print(f"   🏛️  Chefs de département: {roles_count['department_head']}")
    print(f"   👨‍🏫 Enseignants: {roles_count['teacher']}")
    print(f"   👨‍🎓 Étudiants: {roles_count['student']}")
    print(f"   📊 TOTAL: {sum(roles_count.values())}")
    
    print(f"\n🏛️  INFRASTRUCTURE:")
    print(f"   🏛️  Départements: {Department.objects.count()}")
    print(f"   📚 Programmes: {Program.objects.count()}")
    print(f"   🏢 Salles: {Room.objects.count()}")
    print(f"   📖 Matières: {Subject.objects.count()}")
    
    # Générer fichier final
    accounts_file = "comptes_utilisateurs_FINAL.txt"
    with open(accounts_file, 'w', encoding='utf-8') as f:
        f.write("🎓 UNIVERSITÉ - BASE DE DONNÉES COMPLÈTE APPGET\n")
        f.write("="*60 + "\n\n")
        
        f.write("🚀 COMPTES DE TEST PRINCIPAUX:\n")
        f.write("-" * 40 + "\n")
        f.write("👑 Admin principal: admin@university.ma / admin123\n")
        f.write("👑 Super admin: superadmin@university.ma / super123\n") 
        f.write("🏛️  Chef ISEN: karim.mansouri@university.ma / chef2024\n")
        f.write("👨‍🏫 Prof: prof.alami@university.ma / prof123\n")
        f.write("👨‍🎓 Étudiant: ahmed.berrada@etu.university.ma / etudiant123\n\n")
        
        f.write("📊 STATISTIQUES FINALES:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total utilisateurs: {sum(roles_count.values())}\n")
        f.write(f"Départements: {Department.objects.count()}\n")
        f.write(f"Programmes: {Program.objects.count()}\n") 
        f.write(f"Salles: {Room.objects.count()}\n")
        f.write(f"Matières: {Subject.objects.count()}\n")
        f.write(f"Emplois du temps: {Schedule.objects.count()}\n\n")
        
        f.write("💡 TOUS LES MOTS DE PASSE PAR DÉFAUT:\n")
        f.write("-" * 40 + "\n")
        f.write("👑 Administrateurs: admin2024\n")
        f.write("🏛️  Chefs département: chef2024\n")
        f.write("👨‍🏫 Enseignants: prof2024\n")
        f.write("👨‍🎓 Étudiants: etudiant2024\n")
    
    print(f"📁 Fichier final créé: {accounts_file}")
    
    print("\n🎯 PRÊT POUR LES TESTS!")
    print("Démarrez l'application avec: .\\start_servers.ps1")
    print("Puis testez sur: http://localhost:3000/login")

if __name__ == "__main__":
    fix_and_create_remaining_students()
    generate_final_summary()
