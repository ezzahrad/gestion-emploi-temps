# reset_complete.py - Reset complet de toutes les migrations
import os
import shutil
import django
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"Erreur de configuration Django: {e}")

from django.core.management import execute_from_command_line
from pathlib import Path

def reset_complete():
    print("🚨 RESET COMPLET DE TOUTES LES MIGRATIONS")
    print("="*50)
    
    # 1. Supprimer la base SQLite
    db_file = Path("db.sqlite3")
    if db_file.exists():
        db_file.unlink()
        print("✅ Base SQLite supprimée")
    
    # 2. Apps à nettoyer
    apps = ['core', 'authentication', 'schedule', 'notifications']
    
    for app in apps:
        migrations_dir = Path(app) / "migrations"
        if migrations_dir.exists():
            print(f"🧹 Nettoyage des migrations de {app}")
            
            # Supprimer tous les fichiers sauf __init__.py
            for file in migrations_dir.glob("*.py"):
                if file.name != "__init__.py":
                    file.unlink()
                    print(f"  ❌ {file.name}")
            
            # S'assurer que __init__.py existe
            init_file = migrations_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                print(f"  ✅ __init__.py créé pour {app}")
    
    # 3. Créer les migrations dans l'ordre
    print("\n📝 Création des nouvelles migrations...")
    
    migration_order = ['authentication', 'core', 'schedule', 'notifications']
    
    for app in migration_order:
        try:
            print(f"Création des migrations pour {app}...")
            execute_from_command_line(['manage.py', 'makemigrations', app])
        except Exception as e:
            print(f"⚠️  Erreur pour {app}: {e}")
            continue
    
    # 4. Migration finale pour capturer tout
    try:
        print("Vérification finale des migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
    except Exception as e:
        print(f"⚠️  Erreur migration finale: {e}")
    
    # 5. Appliquer les migrations
    print("\n🗃️  Application des migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False
    
    print("\n" + "="*50)
    print("🎉 RESET TERMINÉ!")
    print("Vous pouvez maintenant créer un superutilisateur avec:")
    print("  python manage.py createsuperuser")
    
    return True

if __name__ == "__main__":
    reset_complete()
