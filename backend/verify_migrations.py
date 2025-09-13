#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de vérification post-migration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_migrations():
    """Vérifier l'état des migrations"""
    print("🔍 VÉRIFICATION DES MIGRATIONS")
    print("="*50)
    
    # Vérifier que les fichiers de migration existent
    apps_to_check = ['authentication', 'core', 'schedule', 'notifications']
    
    for app in apps_to_check:
        migration_dir = Path(f"{app}/migrations")
        if not migration_dir.exists():
            print(f"❌ Répertoire de migration manquant: {migration_dir}")
            return False
            
        migrations = list(migration_dir.glob("*.py"))
        migrations = [m for m in migrations if m.name != "__init__.py"]
        
        if not migrations:
            print(f"❌ Aucune migration trouvée pour {app}")
            return False
        else:
            print(f"✅ {app}: {len(migrations)} migration(s)")
            for migration in migrations:
                print(f"   - {migration.name}")
    
    # Vérifier l'état avec Django
    try:
        result = subprocess.run(
            ["python", "manage.py", "showmigrations"], 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"\n📋 ÉTAT DES MIGRATIONS:")
            print("="*50)
            print(result.stdout)
            
            # Vérifier qu'il n'y a pas de migrations non appliquées
            if "[ ]" in result.stdout:
                print("⚠️  ATTENTION: Des migrations ne sont pas appliquées!")
                print("Exécutez: python manage.py migrate")
                return False
            else:
                print("✅ Toutes les migrations sont appliquées")
                
        else:
            print(f"❌ Erreur lors de la vérification: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False
    
    return True

def test_model_imports():
    """Tester l'import des modèles"""
    print(f"\n🧪 TEST D'IMPORT DES MODÈLES")
    print("="*50)
    
    try:
        # Test d'import des modèles
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
        import django
        django.setup()
        
        from authentication.models import User
        from core.models import Department, Program, Room, Subject, Teacher, Student
        from schedule.models import Schedule, Absence, MakeupSession
        from notifications.models import Notification
        
        print("✅ Tous les modèles importés avec succès")
        
        # Tester la création d'objets simples
        print("\n🔧 TEST DE CRÉATION D'OBJETS")
        print("-" * 30)
        
        # Test Department
        dept_count = Department.objects.count()
        print(f"✅ Départements en base: {dept_count}")
        
        # Test User
        user_count = User.objects.count()
        print(f"✅ Utilisateurs en base: {user_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'import: {e}")
        return False

def main():
    print("🚀 VÉRIFICATION POST-MIGRATION - appGET")
    print("="*50)
    
    if not os.path.exists("manage.py"):
        print("❌ Erreur: Ce script doit être exécuté dans le répertoire backend")
        return
    
    # Test 1: Vérifier les migrations
    if not check_migrations():
        print("\n❌ ÉCHEC: Problème avec les migrations")
        return
    
    # Test 2: Tester l'import des modèles  
    if not test_model_imports():
        print("\n❌ ÉCHEC: Problème avec les modèles")
        return
    
    print(f"\n{'='*50}")
    print("🎉 VÉRIFICATION RÉUSSIE!")
    print("Votre application est prête à être utilisée!")
    print(f"{'='*50}")
    
    print(f"\n📋 PROCHAINES ÉTAPES:")
    print("1. Créer un superutilisateur: python manage.py createsuperuser")
    print("2. Lancer le serveur: python manage.py runserver")
    print("3. Accéder à l'admin: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()
