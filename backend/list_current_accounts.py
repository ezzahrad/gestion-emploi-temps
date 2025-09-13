# list_current_accounts.py - Lister tous les comptes disponibles actuellement
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from authentication.models import User
from core.models import Department

def list_current_accounts():
    """Lister tous les comptes actuellement disponibles"""
    print("🔍 COMPTES UTILISATEURS ACTUELLEMENT DISPONIBLES")
    print("="*80)
    
    # Comptes de test rapides encore présents
    quick_accounts = [
        ('admin@university.ma', 'admin123'),
        ('superadmin@university.ma', 'super123'),
        ('prof.alami@university.ma', 'prof123'),
        ('prof.tazi@university.ma', 'prof123'),
        ('ahmed.berrada@etu.university.ma', 'etudiant123'),
        ('zineb.chraibi@etu.university.ma', 'etudiant123'),
        ('youssef.idrissi@etu.university.ma', 'etudiant123'),
    ]
    
    print("👑 COMPTES ADMINISTRATEURS:")
    print("-" * 50)
    admins = User.objects.filter(role='admin').order_by('email')
    for admin in admins:
        # Deviner le mot de passe selon le pattern
        if any(email in admin.email for email, _ in quick_accounts):
            password = next((pwd for email, pwd in quick_accounts if email == admin.email), 'admin2024')
        else:
            password = 'admin2024'
            
        print(f"📧 {admin.email}")
        print(f"👤 {admin.first_name} {admin.last_name}")
        print(f"🔑 Mot de passe: {password}")
        print(f"📊 Statut: {'🟢 Actif' if admin.is_active else '🔴 Inactif'}")
        print("-" * 30)
    
    print("\n🏛️  CHEFS DE DÉPARTEMENT:")
    print("-" * 50)
    heads = User.objects.filter(role='department_head').order_by('email')
    for head in heads:
        dept = Department.objects.filter(head=head).first()
        print(f"📧 {head.email}")
        print(f"👤 {head.first_name} {head.last_name}")
        print(f"🏛️  Département: {dept.name if dept else 'N/A'}")
        print(f"🔑 Mot de passe: chef2024")
        print(f"📊 Statut: {'🟢 Actif' if head.is_active else '🔴 Inactif'}")
        print("-" * 30)
    
    print("\n👨‍🏫 ENSEIGNANTS (échantillon):")
    print("-" * 50)
    teachers = User.objects.filter(role='teacher').order_by('email')[:5]
    for teacher in teachers:
        # Deviner le mot de passe
        if any(email in teacher.email for email, _ in quick_accounts):
            password = next((pwd for email, pwd in quick_accounts if email == teacher.email), 'prof2024')
        else:
            password = 'prof2024'
            
        print(f"📧 {teacher.email}")
        print(f"👤 {teacher.first_name} {teacher.last_name}")
        print(f"🔑 Mot de passe: {password}")
        print(f"📊 Statut: {'🟢 Actif' if teacher.is_active else '🔴 Inactif'}")
        print("-" * 30)
    
    print("\n👨‍🎓 ÉTUDIANTS (échantillon):")
    print("-" * 50)
    students = User.objects.filter(role='student').order_by('email')[:5]
    for student in students:
        # Deviner le mot de passe
        if any(email in student.email for email, _ in quick_accounts):
            password = next((pwd for email, pwd in quick_accounts if email == student.email), 'etudiant2024')
        else:
            password = 'etudiant2024'
            
        print(f"📧 {student.email}")
        print(f"👤 {student.first_name} {student.last_name}")
        print(f"🔑 Mot de passe: {password}")
        print(f"📊 Statut: {'🟢 Actif' if student.is_active else '🔴 Inactif'}")
        print("-" * 30)
    
    print("\n🎯 COMPTES RECOMMANDÉS POUR LES TESTS:")
    print("="*60)
    
    # Trouver les meilleurs comptes de test
    best_admin = User.objects.filter(role='admin', is_active=True).first()
    best_head = User.objects.filter(role='department_head', is_active=True).first()
    best_teacher = User.objects.filter(role='teacher', is_active=True).first()
    best_student = User.objects.filter(role='student', is_active=True).first()
    
    if best_admin:
        admin_pwd = 'admin123' if 'admin@university.ma' == best_admin.email else 'admin2024'
        print(f"👑 Admin: {best_admin.email} / {admin_pwd}")
    
    if best_head:
        print(f"🏛️  Chef: {best_head.email} / chef2024")
    
    if best_teacher:
        teacher_pwd = 'prof123' if any(email in best_teacher.email for email, _ in quick_accounts) else 'prof2024'
        print(f"👨‍🏫 Prof: {best_teacher.email} / {teacher_pwd}")
    
    if best_student:
        student_pwd = 'etudiant123' if any(email in best_student.email for email, _ in quick_accounts) else 'etudiant2024'
        print(f"👨‍🎓 Étudiant: {best_student.email} / {student_pwd}")
    
    print("\n📊 STATISTIQUES:")
    print("-" * 30)
    print(f"👑 Administrateurs: {User.objects.filter(role='admin').count()}")
    print(f"🏛️  Chefs département: {User.objects.filter(role='department_head').count()}")
    print(f"👨‍🏫 Enseignants: {User.objects.filter(role='teacher').count()}")
    print(f"👨‍🎓 Étudiants: {User.objects.filter(role='student').count()}")
    print(f"📊 TOTAL: {User.objects.count()}")

def test_authentication_api():
    """Tester l'API d'authentification avec les bons comptes"""
    print("\n🧪 TEST DE L'API D'AUTHENTIFICATION")
    print("="*50)
    
    import requests
    
    # Trouver un compte admin pour tester
    admin = User.objects.filter(role='admin', is_active=True).first()
    if not admin:
        print("❌ Aucun compte admin trouvé")
        return
    
    # Deviner le mot de passe
    password = 'admin123' if admin.email == 'admin@university.ma' else 'admin2024'
    
    print(f"🧪 Test de connexion avec {admin.email} / {password}")
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                               json={'email': admin.email, 'password': password},
                               headers={'Content-Type': 'application/json'})
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Réponse: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ API d'authentification fonctionne !")
        else:
            print("❌ Problème avec l'API d'authentification")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        print("💡 Assurez-vous que le serveur Django fonctionne")

if __name__ == "__main__":
    list_current_accounts()
    test_authentication_api()
