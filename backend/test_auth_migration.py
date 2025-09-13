"""
Test de création des migrations authentication
"""
import os
import django
from django.core.management import execute_from_command_line

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')

try:
    django.setup()
    print("✅ Django configuré")
    
    # Test création migration authentication
    print("\n📝 Création migration authentication...")
    execute_from_command_line(['manage.py', 'makemigrations', 'authentication'])
    print("✅ Migration authentication créée")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
