#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de nettoyage et résolution DÉFINITIVE des migrations
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description, check_error=True):
    """Execute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"ÉTAPE: {description}")
    print(f"{'='*60}")
    print(f"Commande: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ SUCCÈS")
            if result.stdout.strip():
                print("SORTIE:")
                print(result.stdout)
        else:
            print("❌ ERREUR")
            if result.stderr.strip():
                print("ERREUR:")
                print(result.stderr)
            if result.stdout.strip():
                print("SORTIE:")
                print(result.stdout)
            if check_error:
                return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        if check_error:
            return False
    
    return True

def clean_migrations():
    """Nettoie toutes les migrations existantes"""
    print("\n🧹 NETTOYAGE COMPLET DES MIGRATIONS")
    print("="*50)
    
    apps = ['authentication', 'core', 'schedule', 'notifications']
    
    for app in apps:
        migrations_dir = Path(f"{app}/migrations")
        if migrations_dir.exists():
            # Supprimer tous les fichiers .py sauf __init__.py
            for migration_file in migrations_dir.glob("*.py"):
                if migration_file.name != "__init__.py":
                    try:
                        migration_file.unlink()
                        print(f"🗑️  Supprimé: {migration_file}")
                    except Exception as e:
                        print(f"❌ Erreur suppression {migration_file}: {e}")
            
            # Supprimer le cache
            pycache_dir = migrations_dir / "__pycache__"
            if pycache_dir.exists():
                try:
                    shutil.rmtree(pycache_dir)
                    print(f"🗑️  Cache supprimé: {pycache_dir}")
                except Exception as e:
                    print(f"❌ Erreur suppression cache {pycache_dir}: {e}")
    
    print("✅ Nettoyage terminé")

def verify_models_are_safe():
    """Vérifier que les modèles n'ont pas de dépendances circulaires"""
    print("\n🔍 VÉRIFICATION DES MODÈLES")
    print("="*50)
    
    try:
        # Lire le fichier models.py de core
        with open("core/models.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Vérifier que les champs head sont commentés
        if "head = models.ForeignKey(" in content and not "# head = models.ForeignKey(" in content:
            print("⚠️  Attention: Les champs 'head' ne sont pas commentés")
            print("📝 Correction en cours...")
            
            # Remplacer par la version sécurisée
            content = content.replace(
                "    head = models.ForeignKey(\n        'authentication.User',",
                "    # head = models.ForeignKey(\n    #     'authentication.User',"
            )
            content = content.replace(
                "        on_delete=models.SET_NULL,",
                "    #     on_delete=models.SET_NULL,"
            )
            content = content.replace(
                "        null=True,",
                "    #     null=True,"
            )
            content = content.replace(
                "        blank=True,",
                "    #     blank=True,"
            )
            content = content.replace(
                "        related_name='headed_department'",
                "    #     related_name='headed_department'"
            )
            content = content.replace(
                "        related_name='headed_program'",
                "    #     related_name='headed_program'"
            )
            content = content.replace(
                "    )",
                "    # )"
            )
            
            # Sauvegarder le fichier corrigé
            with open("core/models.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✅ Modèles corrigés")
        else:
            print("✅ Modèles déjà sécurisés")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False
    
    return True

def main():
    print("🚀 NETTOYAGE ET RÉSOLUTION DÉFINITIVE - appGET")
    print("="*60)
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("manage.py"):
        print("❌ Erreur: Ce script doit être exécuté dans le répertoire backend")
        return
    
    # Étape 1: Nettoyage complet
    clean_migrations()
    
    # Étape 2: Vérifier et corriger les modèles
    if not verify_models_are_safe():
        print("❌ Échec de la correction des modèles")
        return
    
    # Étape 3: Créer les migrations de base
    print("\n📝 PHASE 1: Création des migrations de base")
    print("="*50)
    
    if not run_command("python manage.py makemigrations authentication", 
                      "Création des migrations authentication"):
        print("❌ Échec de la création des migrations authentication")
        return
    
    if not run_command("python manage.py makemigrations core", 
                      "Création des migrations core"):
        print("❌ Échec de la création des migrations core")
        return
    
    # Étape 4: Appliquer les migrations de base
    if not run_command("python manage.py migrate", 
                      "Application des migrations de base"):
        print("❌ Échec de l'application des migrations de base")
        return
    
    print("\n🎉 PHASE 1 TERMINÉE: Migrations de base créées et appliquées!")
    
    # Étape 5: Restaurer le modèle complet
    print("\n📝 PHASE 2: Restauration du modèle complet")
    print("="*50)
    
    try:
        if os.path.exists("core/models_complete.py"):
            shutil.copy2("core/models_complete.py", "core/models.py")
            print("✅ Modèle complet restauré")
        else:
            print("❌ Fichier models_complete.py introuvable")
            return
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        return
    
    # Étape 6: Créer la migration pour ajouter les champs head
    if not run_command("python manage.py makemigrations core", 
                      "Création de la migration pour les champs head"):
        print("❌ Échec de la création de la migration pour les champs head")
        return
    
    # Étape 7: Créer les migrations pour schedule et notifications
    if not run_command("python manage.py makemigrations schedule", 
                      "Création des migrations schedule"):
        print("❌ Échec de la création des migrations schedule")
        return
    
    if not run_command("python manage.py makemigrations notifications", 
                      "Création des migrations notifications"):
        print("❌ Échec de la création des migrations notifications")
        return
    
    # Étape 8: Appliquer toutes les migrations
    if not run_command("python manage.py migrate", 
                      "Application de toutes les migrations"):
        print("❌ Échec de l'application des migrations finales")
        return
    
    print(f"\n{'='*60}")
    print("🎉🎉🎉 SUCCÈS COMPLET! 🎉🎉🎉")
    print("Toutes les migrations ont été créées et appliquées avec succès!")
    print(f"{'='*60}")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    run_command("python manage.py showmigrations", 
                "État final des migrations", check_error=False)
    
    print(f"\n📋 PROCHAINES ÉTAPES:")
    print("1. Créer un superutilisateur: python manage.py createsuperuser")
    print("2. Lancer le serveur: python manage.py runserver")
    print("3. Tester l'interface admin: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()
