#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test que tous les modèles sont bien enregistrés dans l'admin
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')

try:
    django.setup()
    
    from django.contrib import admin
    from django.apps import apps
    
    print("🔍 VÉRIFICATION DES MODÈLES ADMIN")
    print("="*50)
    
    # Récupérer tous les modèles enregistrés
    registered_models = admin.site._registry
    
    print(f"\n📊 Total des modèles enregistrés: {len(registered_models)}")
    
    # Grouper par app
    apps_models = {}
    for model, admin_class in registered_models.items():
        app_label = model._meta.app_label
        if app_label not in apps_models:
            apps_models[app_label] = []
        apps_models[app_label].append({
            'model': model,
            'admin': admin_class,
            'name': model._meta.verbose_name
        })
    
    # Afficher par app
    for app_label, models in apps_models.items():
        print(f"\n📱 App: {app_label.upper()}")
        for model_info in models:
            model_name = model_info['name']
            admin_class_name = model_info['admin'].__class__.__name__
            print(f"   ✅ {model_name} ({admin_class_name})")
    
    # Vérifier nos apps spécifiques
    expected_apps = ['authentication', 'core', 'schedule', 'notifications']
    missing_apps = []
    
    for app in expected_apps:
        if app not in apps_models:
            missing_apps.append(app)
        else:
            print(f"\n✅ App '{app}': {len(apps_models[app])} modèle(s)")
    
    if missing_apps:
        print(f"\n❌ Apps manquantes: {', '.join(missing_apps)}")
        print("Vérifiez que les fichiers admin.py existent et sont corrects")
    else:
        print(f"\n🎉 SUCCÈS: Tous les modèles sont enregistrés!")
        print("\nVous pouvez maintenant:")
        print("1. Redémarrer le serveur Django")
        print("2. Aller sur http://127.0.0.1:8000/admin/")
        print("3. Voir tous vos modèles dans l'interface d'administration")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\nVérifiez que:")
    print("1. Vous êtes dans le répertoire backend")
    print("2. Les migrations sont appliquées")
    print("3. Les fichiers admin.py sont corrects")
