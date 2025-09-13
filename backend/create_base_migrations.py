import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line
import sys

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

def create_migrations_step_by_step():
    print("🚀 Création des migrations étape par étape")
    
    try:
        # Étape 1: Créer les migrations pour authentication
        print("\n📝 Étape 1: Création des migrations authentication...")
        execute_from_command_line(['manage.py', 'makemigrations', 'authentication'])
        print("✅ Migrations authentication créées")
        
        # Étape 2: Créer les migrations pour core
        print("\n📝 Étape 2: Création des migrations core...")
        execute_from_command_line(['manage.py', 'makemigrations', 'core'])
        print("✅ Migrations core créées")
        
        # Étape 3: Appliquer les migrations
        print("\n📝 Étape 3: Application des migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées")
        
        print("\n🎉 Migrations de base créées avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = create_migrations_step_by_step()
    if success:
        print("\n📋 Prochaines étapes:")
        print("1. Restaurer les champs 'head' dans core/models.py")
        print("2. Exécuter: python manage.py makemigrations core")
        print("3. Créer les migrations pour schedule et notifications")
        print("4. Appliquer toutes les migrations: python manage.py migrate")
