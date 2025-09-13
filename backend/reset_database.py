#!/usr/bin/env python3
"""
Script pour réinitialiser complètement la base de données AppGET
Usage: python reset_database.py
"""

import os
import sys
import shutil
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appget.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
from django.db import connection
import subprocess

def print_step(step, message):
    """Afficher une étape avec style"""
    print(f"\n{'='*50}")
    print(f"ÉTAPE {step}: {message}")
    print(f"{'='*50}")

def remove_sqlite_db():
    """Supprimer la base SQLite si elle existe"""
    db_file = Path("db.sqlite3")
    if db_file.exists():
        db_file.unlink()
        print("✅ Base de données SQLite supprimée")
    else:
        print("ℹ️  Aucune base SQLite trouvée")

def clean_migrations():
    """Supprimer tous les fichiers de migration sauf __init__.py"""
    print("🧹 Nettoyage des migrations...")
    
    # Trouver tous les dossiers migrations
    migration_dirs = []
    for root, dirs, files in os.walk('.'):
        if 'migrations' in dirs:
            migration_path = os.path.join(root, 'migrations')
            migration_dirs.append(migration_path)
    
    # Nettoyer chaque dossier migrations
    for migration_dir in migration_dirs:
        if os.path.exists(migration_dir):
            for file in os.listdir(migration_dir):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(migration_dir, file)
                    os.remove(file_path)
                    print(f"  ❌ {file_path}")
                elif file.endswith('.pyc'):
                    file_path = os.path.join(migration_dir, file)
                    os.remove(file_path)
    
    print("✅ Migrations nettoyées")

def create_migrations():
    """Créer les nouvelles migrations"""
    print("📝 Création des nouvelles migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✅ Migrations créées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la création des migrations: {e}")
        return False
    return True

def apply_migrations():
    """Appliquer les migrations"""
    print("🗃️  Application des migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'application des migrations: {e}")
        return False
    return True

def create_superuser():
    """Créer un superutilisateur"""
    print("👤 Création d'un superutilisateur...")
    print("Veuillez entrer les informations pour le superutilisateur:")
    
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
        print("✅ Superutilisateur créé avec succès")
    except KeyboardInterrupt:
        print("\n⚠️  Création du superutilisateur annulée")
    except Exception as e:
        print(f"❌ Erreur lors de la création du superutilisateur: {e}")

def load_sample_data():
    """Charger des données d'exemple"""
    choice = input("\n🎯 Voulez-vous charger des données d'exemple? (y/n): ").lower()
    
    if choice == 'y':
        print("📊 Chargement des données d'exemple...")
        try:
            # Créer le fichier de fixtures s'il n'existe pas
            create_sample_fixtures()
            execute_from_command_line(['manage.py', 'loaddata', 'sample_data.json'])
            print("✅ Données d'exemple chargées")
        except Exception as e:
            print(f"⚠️  Impossible de charger les données d'exemple: {e}")

def create_sample_fixtures():
    """Créer des fixtures d'exemple"""
    fixtures_content = '''[
    {
        "model": "core.department",
        "pk": 1,
        "fields": {
            "name": "Informatique",
            "code": "INFO",
            "description": "Département d'Informatique et Sciences du Numérique",
            "is_active": true
        }
    },
    {
        "model": "core.department", 
        "pk": 2,
        "fields": {
            "name": "Mathématiques",
            "code": "MATH",
            "description": "Département de Mathématiques",
            "is_active": true
        }
    },
    {
        "model": "core.program",
        "pk": 1,
        "fields": {
            "name": "Licence Informatique",
            "code": "L-INFO",
            "level": "L3",
            "duration_years": 3,
            "max_students": 50,
            "department": 1,
            "is_active": true
        }
    },
    {
        "model": "core.room",
        "pk": 1,
        "fields": {
            "name": "Amphi A",
            "code": "AMPH-A",
            "room_type": "amphitheater",
            "capacity": 200,
            "building": "Bâtiment Principal",
            "floor": "RDC",
            "equipment": "Projecteur, Micro, Climatisation",
            "department": 1,
            "is_available": true
        }
    },
    {
        "model": "core.timeslot",
        "pk": 1,
        "fields": {
            "day_of_week": 0,
            "start_time": "08:00:00",
            "end_time": "09:30:00", 
            "duration_minutes": 90,
            "is_active": true
        }
    },
    {
        "model": "core.timeslot",
        "pk": 2,
        "fields": {
            "day_of_week": 0,
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "duration_minutes": 90,
            "is_active": true
        }
    }
]'''
    
    with open('sample_data.json', 'w', encoding='utf-8') as f:
        f.write(fixtures_content)

def main():
    """Fonction principale"""
    print("🚀 RÉINITIALISATION DE LA BASE DE DONNÉES APPGET")
    print("=" * 50)
    
    # Confirmation
    confirmation = input("⚠️  ATTENTION: Cette opération va SUPPRIMER toutes les données existantes!\nÊtes-vous sûr de vouloir continuer? (tapez 'OUI' pour confirmer): ")
    
    if confirmation != 'OUI':
        print("❌ Opération annulée")
        return
    
    try:
        # Étape 1: Supprimer l'ancienne base
        print_step(1, "Suppression de l'ancienne base de données")
        remove_sqlite_db()
        
        # Étape 2: Nettoyer les migrations
        print_step(2, "Nettoyage des migrations")
        clean_migrations()
        
        # Étape 3: Créer les nouvelles migrations
        print_step(3, "Création des nouvelles migrations")
        if not create_migrations():
            return
        
        # Étape 4: Appliquer les migrations
        print_step(4, "Application des migrations")
        if not apply_migrations():
            return
        
        # Étape 5: Créer un superutilisateur
        print_step(5, "Création du superutilisateur")
        create_superuser()
        
        # Étape 6: Données d'exemple (optionnel)
        print_step(6, "Données d'exemple (optionnel)")
        load_sample_data()
        
        print("\n" + "=" * 50)
        print("🎉 RÉINITIALISATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 50)
        print("✅ Nouvelle base de données créée")
        print("✅ Tables créées selon la nouvelle structure")
        print("✅ Prêt à démarrer l'application")
        print("\nPour démarrer le serveur:")
        print("  python manage.py runserver")
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        print("💡 Vérifiez que Django est bien installé et configuré")

if __name__ == "__main__":
    main()
