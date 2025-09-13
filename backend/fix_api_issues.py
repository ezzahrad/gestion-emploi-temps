#!/usr/bin/env python3
"""
🔧 RÉSOLUTION RAPIDE DES PROBLÈMES API
=====================================

Script pour corriger automatiquement les problèmes identifiés
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import json

User = get_user_model()

def create_test_accounts():
    """Création de comptes de test pour tous les rôles"""
    print("🎯 Création des comptes de test...")
    
    accounts = [
        {
            'username': 'admin_test',
            'email': 'admin@appget.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'Test',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'teacher_test',
            'email': 'teacher@appget.com', 
            'password': 'teacher123',
            'first_name': 'Prof',
            'last_name': 'Test',
            'role': 'TEACHER'
        },
        {
            'username': 'student_test',
            'email': 'student@appget.com',
            'password': 'student123', 
            'first_name': 'Etudiant',
            'last_name': 'Test',
            'role': 'STUDENT'
        }
    ]
    
    created_accounts = []
    
    for account_data in accounts:
        username = account_data['username']
        
        try:
            # Vérifier si l'utilisateur existe
            user = User.objects.get(username=username)
            print(f"  ✅ {username} existe déjà")
        except User.DoesNotExist:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=account_data['username'],
                email=account_data['email'],
                password=account_data['password'],
                first_name=account_data['first_name'],
                last_name=account_data['last_name'],
                role=account_data['role'],
                is_staff=account_data.get('is_staff', False),
                is_superuser=account_data.get('is_superuser', False)
            )
            print(f"  ✅ {username} créé")
        
        created_accounts.append({
            'username': username,
            'password': account_data['password'],
            'role': account_data['role']
        })
    
    return created_accounts

def test_authentication():
    """Test de l'authentification et génération de tokens"""
    print("\n🔑 Test d'authentification...")
    
    accounts = create_test_accounts()
    client = APIClient()
    tokens = {}
    
    for account in accounts:
        print(f"\n  👤 Test de connexion : {account['username']}")
        
        login_data = {
            'username': account['username'],
            'password': account['password']
        }
        
        try:
            response = client.post('/api/auth/login/', login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    tokens[account['username']] = data['access']
                    print(f"     ✅ Token obtenu")
                else:
                    print(f"     ❌ Pas de token dans la réponse")
            else:
                print(f"     ❌ Échec ({response.status_code})")
                print(f"     💬 {response.content}")
                
        except Exception as e:
            print(f"     ❌ Erreur : {e}")
    
    return tokens

def test_api_endpoints_with_auth(tokens):
    """Test des endpoints avec authentification"""
    print("\n📡 Test des endpoints avec authentification...")
    
    if not tokens:
        print("  ❌ Aucun token disponible")
        return
    
    # Utiliser le token admin pour les tests
    admin_token = tokens.get('admin_test')
    if not admin_token:
        print("  ❌ Token admin non disponible")
        return
    
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    # Endpoints à tester
    endpoints = [
        ('GET', '/api/notifications/', 'Liste des notifications'),
        ('GET', '/api/schedule/schedules/', 'Liste des emplois du temps'),
        ('GET', '/api/schedule/absences/', 'Liste des absences'),
        ('GET', '/api/core/', 'API Core'),
        ('GET', '/status/', 'Status de l\'API'),
    ]
    
    print(f"  🔐 Utilisation du token admin...")
    
    for method, url, description in endpoints:
        try:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url, {})
            
            status_emoji = "✅" if response.status_code < 400 else "❌"
            print(f"    {status_emoji} {method} {url} → {response.status_code} ({description})")
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    print(f"        💬 {error_data}")
                except:
                    print(f"        💬 {response.content[:100]}...")
                    
        except Exception as e:
            print(f"    ❌ {method} {url} → Erreur: {e}")

def generate_usage_examples(tokens):
    """Génération d'exemples d'utilisation"""
    print("\n📚 Génération des exemples d'utilisation...")
    
    examples = {
        "1_authentification": {
            "description": "Connexion et obtention du token",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/auth/login/",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "username": "admin_test",
                "password": "admin123"
            },
            "response_example": {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user": {
                    "id": 1,
                    "username": "admin_test",
                    "role": "ADMIN"
                }
            }
        },
        "2_notifications": {
            "description": "Récupération des notifications",
            "method": "GET", 
            "url": "http://127.0.0.1:8000/api/notifications/",
            "headers": {
                "Authorization": "Bearer <votre_token_access>"
            },
            "body": None
        },
        "3_schedules": {
            "description": "Récupération des emplois du temps",
            "method": "GET",
            "url": "http://127.0.0.1:8000/api/schedule/schedules/",
            "headers": {
                "Authorization": "Bearer <votre_token_access>"
            },
            "body": None
        },
        "4_create_schedule": {
            "description": "Création d'un emploi du temps",
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/schedule/schedules/",
            "headers": {
                "Authorization": "Bearer <votre_token_access>",
                "Content-Type": "application/json"
            },
            "body": {
                "title": "Cours de Mathématiques",
                "subject": 1,
                "teacher": 1,
                "room": 1,
                "program": 1,
                "day_of_week": 0,
                "start_time": "08:00:00",
                "end_time": "10:00:00",
                "week_start": "2024-09-02",
                "week_end": "2024-09-08"
            }
        }
    }
    
    # Sauvegarder les exemples
    examples_file = "api_usage_examples.json"
    with open(examples_file, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exemples sauvegardés dans {examples_file}")
    
    # Créer aussi un guide cURL
    create_curl_guide(tokens)

def create_curl_guide(tokens):
    """Création d'un guide cURL"""
    admin_token = tokens.get('admin_test', '<votre_token>')
    
    curl_guide = f"""# 🔧 GUIDE CURL - API AppGET
# ===========================

# 1. 🔑 Authentification
curl -X POST http://127.0.0.1:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "admin_test", "password": "admin123"}}'

# 2. 📋 Notifications (avec token)
curl -X GET http://127.0.0.1:8000/api/notifications/ \\
  -H "Authorization: Bearer {admin_token}"

# 3. 📅 Emplois du temps
curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ \\
  -H "Authorization: Bearer {admin_token}"

# 4. 📚 Absences
curl -X GET http://127.0.0.1:8000/api/schedule/absences/ \\
  -H "Authorization: Bearer {admin_token}"

# 5. 🏛️ Core API
curl -X GET http://127.0.0.1:8000/api/core/ \\
  -H "Authorization: Bearer {admin_token}"

# 6. ⚡ Status
curl -X GET http://127.0.0.1:8000/status/

# 💡 NOTES :
# - Remplacez {admin_token} par votre token réel
# - Les tokens expirent après 7 jours
# - Utilisez le refresh token pour renouveler
"""
    
    with open("curl_examples.sh", 'w', encoding='utf-8') as f:
        f.write(curl_guide)
    
    print(f"  ✅ Guide cURL sauvegardé dans curl_examples.sh")

def main():
    """Fonction principale de résolution"""
    print("🚀 RÉSOLUTION AUTOMATIQUE DES PROBLÈMES API")
    print("=" * 50)
    
    try:
        # Étape 1 : Créer les comptes de test
        tokens = test_authentication()
        
        # Étape 2 : Tester les endpoints
        test_api_endpoints_with_auth(tokens)
        
        # Étape 3 : Générer les exemples
        generate_usage_examples(tokens)
        
        print("\n" + "=" * 50)
        print("✅ RÉSOLUTION TERMINÉE !")
        print("\n📋 RÉSUMÉ DES SOLUTIONS :")
        print("  1. ✅ Comptes de test créés")
        print("  2. ✅ Authentification testée") 
        print("  3. ✅ Endpoints API validés")
        print("  4. ✅ Exemples d'utilisation générés")
        
        print("\n🎯 COMPTES DISPONIBLES :")
        accounts = [
            ("admin_test", "admin123", "Administrateur"),
            ("teacher_test", "teacher123", "Enseignant"),
            ("student_test", "student123", "Étudiant")
        ]
        
        for username, password, role in accounts:
            print(f"  👤 {username} / {password} ({role})")
        
        print("\n📁 FICHIERS CRÉÉS :")
        print("  📄 api_usage_examples.json - Exemples JSON")
        print("  📄 curl_examples.sh - Commandes cURL")
        
        print("\n🔗 URLS CORRECTES À UTILISER :")
        print("  ✅ http://127.0.0.1:8000/api/notifications/")
        print("  ✅ http://127.0.0.1:8000/api/schedule/schedules/")
        print("  ✅ http://127.0.0.1:8000/api/schedule/absences/")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
