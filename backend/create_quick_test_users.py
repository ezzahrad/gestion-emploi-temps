# create_quick_test_users.py - Créer rapidement des utilisateurs de test
import os
import django
from django.contrib.auth.hashers import make_password

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from authentication.models import User

def create_quick_test_users():
    """Créer rapidement des utilisateurs de test pour l'authentification"""
    print("⚡ Création rapide d'utilisateurs de test...")
    
    test_users = [
        # Administrateurs
        {
            'first_name': 'Admin',
            'last_name': 'Principal', 
            'email': 'admin@university.ma',
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'is_staff': True
        },
        {
            'first_name': 'Super',
            'last_name': 'Administrateur',
            'email': 'superadmin@university.ma', 
            'username': 'superadmin',
            'password': 'super123',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        },
        
        # Chef de département
        {
            'first_name': 'Hassan',
            'last_name': 'BENALI',
            'email': 'chef.info@university.ma',
            'username': 'chef.info',
            'password': 'chef123',
            'role': 'department_head'
        },
        
        # Enseignants
        {
            'first_name': 'Mohamed',
            'last_name': 'ALAMI',
            'email': 'prof.alami@university.ma',
            'username': 'prof.alami', 
            'password': 'prof123',
            'role': 'teacher'
        },
        {
            'first_name': 'Fatima',
            'last_name': 'TAZI',
            'email': 'prof.tazi@university.ma',
            'username': 'prof.tazi',
            'password': 'prof123', 
            'role': 'teacher'
        },
        
        # Étudiants
        {
            'first_name': 'Ahmed',
            'last_name': 'BERRADA',
            'email': 'ahmed.berrada@etu.university.ma',
            'username': 'ahmed.berrada',
            'password': 'etudiant123',
            'role': 'student'
        },
        {
            'first_name': 'Zineb', 
            'last_name': 'CHRAIBI',
            'email': 'zineb.chraibi@etu.university.ma',
            'username': 'zineb.chraibi',
            'password': 'etudiant123',
            'role': 'student'
        },
        {
            'first_name': 'Youssef',
            'last_name': 'IDRISSI', 
            'email': 'youssef.idrissi@etu.university.ma',
            'username': 'youssef.idrissi',
            'password': 'etudiant123',
            'role': 'student'
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': make_password(user_data['password']),
                'role': user_data['role'],
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
                'is_active': True
            }
        )
        
        if created:
            created_users.append((user, user_data['password']))
            print(f"✅ {user.first_name} {user.last_name} ({user.role})")
        else:
            print(f"ℹ️  {user.first_name} {user.last_name} existe déjà")
    
    # Générer le fichier de comptes
    with open('comptes_test_rapide.txt', 'w', encoding='utf-8') as f:
        f.write("🎓 COMPTES DE TEST RAPIDE - APPGET\n")
        f.write("="*50 + "\n\n")
        
        roles = {
            'admin': '👑 ADMINISTRATEURS',
            'department_head': '🏛️  CHEFS DE DÉPARTEMENT', 
            'teacher': '👨‍🏫 ENSEIGNANTS',
            'student': '👨‍🎓 ÉTUDIANTS'
        }
        
        for role, title in roles.items():
            users = User.objects.filter(role=role)
            if users:
                f.write(f"{title}\n")
                f.write("-" * 40 + "\n")
                
                for user in users:
                    # Trouver le mot de passe depuis les données de test
                    password = 'Voir script'
                    for user_data in test_users:
                        if user_data['email'] == user.email:
                            password = user_data['password']
                            break
                    
                    f.write(f"Nom: {user.first_name} {user.last_name}\n")
                    f.write(f"Email: {user.email}\n")
                    f.write(f"Mot de passe: {password}\n")
                    f.write("-" * 20 + "\n")
                f.write("\n")
    
    print(f"\n✅ {len(created_users)} nouveaux utilisateurs créés")
    print(f"📁 Fichier généré: comptes_test_rapide.txt")
    print(f"📊 Total utilisateurs: {User.objects.count()}")
    
    print("\n🚀 COMPTES PRÊTS POUR LES TESTS:")
    print("="*50)
    print("👑 Admin: admin@university.ma / admin123")
    print("🏛️  Chef: chef.info@university.ma / chef123") 
    print("👨‍🏫 Prof: prof.alami@university.ma / prof123")
    print("👨‍🎓 Étudiant: ahmed.berrada@etu.university.ma / etudiant123")
    
    return created_users

if __name__ == "__main__":
    create_quick_test_users()
