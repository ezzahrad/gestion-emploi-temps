#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script automatisé pour résoudre les problèmes de migrations avec dépendances circulaires
"""

import os
import sys
import subprocess
import shutil

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

def backup_file(filepath):
    """Créer une sauvegarde du fichier"""
    backup_path = f"{filepath}.backup"
    if os.path.exists(filepath):
        shutil.copy2(filepath, backup_path)
        print(f"📁 Sauvegarde créée: {backup_path}")
        return True
    return False

def restore_complete_models():
    """Restaurer le modèle complet avec les champs head"""
    models_path = "core/models.py"
    complete_models_path = "core/models_complete.py"
    
    if os.path.exists(complete_models_path):
        backup_file(models_path)
        shutil.copy2(complete_models_path, models_path)
        print("✅ Modèle complet restauré")
        return True
    else:
        print(f"❌ Fichier {complete_models_path} introuvable")
        return False

def main():
    print("🚀 SCRIPT DE RÉSOLUTION DES MIGRATIONS - appGET")
    print("Ce script va résoudre les problèmes de dépendances circulaires")
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("manage.py"):
        print("❌ Erreur: Ce script doit être exécuté dans le répertoire backend")
        return
    
    # Étape 1: Nettoyer les migrations existantes (déjà fait)
    print("\n🧹 Les migrations ont déjà été nettoyées")
    
    # Étape 2: Créer les migrations de base (sans champs head)
    print("\n📝 PHASE 1: Création des migrations de base")
    
    if not run_command("python manage.py makemigrations authentication", 
                      "Création des migrations authentication"):
        print("❌ Échec de la création des migrations authentication")
        return
    
    if not run_command("python manage.py makemigrations core", 
                      "Création des migrations core"):
        print("❌ Échec de la création des migrations core")
        return
    
    # Étape 3: Appliquer les migrations de base
    if not run_command("python manage.py migrate", 
                      "Application des migrations de base"):
        print("❌ Échec de l'application des migrations de base")
        return
    
    print("\n🎉 PHASE 1 TERMINÉE: Migrations de base créées et appliquées!")
    
    # Étape 4: Restaurer le modèle complet
    print("\n📝 PHASE 2: Restauration du modèle complet")
    
    if not restore_complete_models():
        print("❌ Échec de la restauration du modèle complet")
        return
    
    # Étape 5: Créer la migration pour ajouter les champs head
    if not run_command("python manage.py makemigrations core", 
                      "Création de la migration pour les champs head"):
        print("❌ Échec de la création de la migration pour les champs head")
        return
    
    # Étape 6: Créer les migrations pour schedule et notifications
    if not run_command("python manage.py makemigrations schedule", 
                      "Création des migrations schedule"):
        print("❌ Échec de la création des migrations schedule")
        return
    
    if not run_command("python manage.py makemigrations notifications", 
                      "Création des migrations notifications"):
        print("❌ Échec de la création des migrations notifications")
        return
    
    # Étape 7: Appliquer toutes les migrations
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

if __name__ == "__main__":
    main()
