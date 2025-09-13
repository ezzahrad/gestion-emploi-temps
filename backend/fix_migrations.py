#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour résoudre les problèmes de migrations avec les dépendances circulaires
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Execute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"ÉTAPE: {description}")
    print(f"{'='*60}")
    print(f"Commande: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ SUCCÈS")
            if result.stdout:
                print("SORTIE:")
                print(result.stdout)
        else:
            print("❌ ERREUR")
            if result.stderr:
                print("ERREUR:")
                print(result.stderr)
            if result.stdout:
                print("SORTIE:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False
    
    return True

def main():
    print("🚀 Résolution des problèmes de migrations pour appGET")
    
    # Étape 1: Créer les migrations de base
    if not run_command("python manage.py makemigrations authentication", 
                      "Création des migrations authentication"):
        return
    
    if not run_command("python manage.py makemigrations core", 
                      "Création des migrations core"):
        return
    
    # Étape 2: Appliquer ces migrations
    if not run_command("python manage.py migrate", 
                      "Application des migrations de base"):
        return
    
    print("\n🎉 Migrations de base créées avec succès!")
    print("\nMaintenant, nous allons restaurer les champs head...")
    
    # Instructions pour la suite
    print(f"\n{'='*60}")
    print("PROCHAINES ÉTAPES:")
    print("1. Restaurer les champs 'head' dans core/models.py")
    print("2. Créer une migration pour ajouter ces champs")
    print("3. Créer les migrations pour schedule et notifications")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
