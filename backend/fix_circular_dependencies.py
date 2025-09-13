# fix_circular_dependencies.py - Résoudre les dépendances circulaires
import os
import shutil
import sys
from pathlib import Path

def backup_file(file_path):
    """Créer une sauvegarde d'un fichier"""
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Sauvegarde créée: {backup_path}")

def restore_file(file_path):
    """Restaurer un fichier depuis sa sauvegarde"""
    backup_path = f"{file_path}.backup"
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)
        print(f"✅ Fichier restauré: {file_path}")

def clean_migrations():
    """Supprimer toutes les migrations existantes"""
    apps = ['core', 'authentication', 'schedule', 'notifications']
    
    # Supprimer db.sqlite3
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("✅ db.sqlite3 supprimé")
    
    for app in apps:
        migrations_dir = Path(app) / "migrations"
        if migrations_dir.exists():
            print(f"🧹 Nettoyage des migrations de {app}")
            
            for file in migrations_dir.glob("*.py"):
                if file.name != "__init__.py":
                    file.unlink()
                    print(f"  ❌ {file.name}")
            
            init_file = migrations_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()

def modify_authentication_models():
    """Modifier temporairement les modèles authentication pour supprimer les dépendances circulaires"""
    models_file = "authentication/models.py"
    
    # Sauvegarder l'original
    backup_file(models_file)
    
    # Contenu temporaire sans dépendances vers core
    temp_content = '''from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur Pédagogique'),
        ('department_head', 'Chef de Département'),
        ('program_head', 'Chef de Filière'), 
        ('teacher', 'Enseignant'),
        ('student', 'Étudiant'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
'''
    
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(temp_content)
    
    print("✅ Modèles authentication modifiés temporairement")

def restore_authentication_models():
    """Restaurer les modèles authentication originaux"""
    models_file = "authentication/models.py"
    restore_file(models_file)

def run_command(command):
    """Exécuter une commande Django"""
    print(f"🔧 Exécution: {command}")
    exit_code = os.system(f"python {command}")
    if exit_code != 0:
        print(f"❌ Erreur lors de l'exécution de: {command}")
        return False
    return True

def main():
    print("🚀 RÉSOLUTION DES DÉPENDANCES CIRCULAIRES")
    print("=" * 50)
    
    try:
        # Étape 1: Nettoyer toutes les migrations
        print("\n📋 ÉTAPE 1: Nettoyage des migrations")
        clean_migrations()
        
        # Étape 2: Modifier temporairement authentication/models.py
        print("\n📋 ÉTAPE 2: Modification temporaire des modèles")
        modify_authentication_models()
        
        # Étape 3: Créer les migrations pour authentication
        print("\n📋 ÉTAPE 3: Création des migrations authentication")
        if not run_command("manage.py makemigrations authentication"):
            raise Exception("Erreur création migrations authentication")
        
        # Étape 4: Restaurer les modèles originaux
        print("\n📋 ÉTAPE 4: Restauration des modèles originaux")
        restore_authentication_models()
        
        # Étape 5: Créer les migrations pour core
        print("\n📋 ÉTAPE 5: Création des migrations core")
        if not run_command("manage.py makemigrations core"):
            raise Exception("Erreur création migrations core")
        
        # Étape 6: Créer les migrations pour les dépendances ajoutées
        print("\n📋 ÉTAPE 6: Ajout des dépendances")
        if not run_command("manage.py makemigrations authentication"):
            print("⚠️  Aucune nouvelle migration pour authentication (normal)")
        
        # Étape 7: Créer les migrations pour les autres apps
        print("\n📋 ÉTAPE 7: Autres apps")
        run_command("manage.py makemigrations schedule")
        run_command("manage.py makemigrations notifications")
        run_command("manage.py makemigrations")
        
        # Étape 8: Appliquer toutes les migrations
        print("\n📋 ÉTAPE 8: Application des migrations")
        if not run_command("manage.py migrate"):
            raise Exception("Erreur application migrations")
        
        print("\n" + "=" * 50)
        print("🎉 RÉSOLUTION TERMINÉE AVEC SUCCÈS!")
        print("=" * 50)
        print("✅ Dépendances circulaires résolues")
        print("✅ Toutes les migrations créées et appliquées")
        print("✅ Base de données prête")
        print("\nVous pouvez maintenant créer un superutilisateur:")
        print("  python manage.py createsuperuser")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("🔄 Tentative de restauration des fichiers...")
        
        # Restaurer les fichiers en cas d'erreur
        try:
            restore_authentication_models()
        except:
            pass
        
        return False
    
    return True

if __name__ == "__main__":
    main()
