#!/usr/bin/env python3
"""
🔧 CORRECTION RAPIDE - Problème testserver
=========================================

Script pour corriger le problème DisallowedHost avec testserver
et tester l'API avec les vrais endpoints.
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def fix_allowed_hosts():
    """Ajouter testserver aux ALLOWED_HOSTS temporairement"""
    print_header("CORRECTION DES ALLOWED_HOSTS")
    
    settings_file = "schedule_management/settings.py"
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si testserver est déjà présent
        if "'testserver'" in content:
            print("✅ 'testserver' est déjà dans ALLOWED_HOSTS")
            return True
        
        # Ajouter testserver
        old_line = "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']"
        new_line = "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'testserver']"
        
        if old_line in content:
            new_content = content.replace(old_line, new_line)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 'testserver' ajouté aux ALLOWED_HOSTS")
            print("💡 Redémarrez le serveur Django pour appliquer les changements")
            return True
        else:
            print("❌ Impossible de trouver la ligne ALLOWED_HOSTS à modifier")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la modification : {e}")
        return False

def test_with_real_server():
    """Tester avec le vrai serveur Django"""
    print_header("TEST AVEC SERVEUR RÉEL")
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔑 Test d'authentification avec le serveur réel...")
    
    # Test de connexion
    login_data = {
        'username': 'admin_test',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{base_url}/api/auth/login/', json=login_data)
        print(f"  📍 POST /api/auth/login/ → {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access' in data:
                token = data['access']
                print(f"  ✅ Token JWT reçu")
                
                # Tester les API avec le token
                headers = {'Authorization': f'Bearer {token}'}
                
                print(f"\n📋 Test des API avec authentification :")
                test_urls = [
                    '/api/notifications/',
                    '/api/schedule/schedules/',
                    '/api/core/departments/',
                    '/api/core/programs/',
                ]
                
                for url in test_urls:
                    try:
                        response = requests.get(f'{base_url}{url}', headers=headers)
                        status_emoji = "✅" if response.status_code < 400 else "❌"
                        print(f"  {status_emoji} {url} → {response.status_code}")
                        
                        if response.status_code == 403:
                            print(f"      💡 Problème de permissions")
                        elif response.status_code == 404:
                            print(f"      💡 Endpoint non trouvé")
                            
                    except requests.exceptions.ConnectionError:
                        print(f"  ❌ {url} → Serveur non accessible")
                        print(f"      💡 Assurez-vous que le serveur Django tourne")
                        break
                        
                return token
            else:
                print(f"  ❌ Pas de token dans la réponse")
        else:
            print(f"  ❌ Échec de l'authentification")
            print(f"      Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Impossible de se connecter au serveur")
        print(f"  💡 Démarrez le serveur avec: python manage.py runserver")
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test : {e}")
    
    return None

def create_curl_examples_with_token(token=None):
    """Créer des exemples cURL avec un vrai token"""
    print_header("GÉNÉRATION D'EXEMPLES CURL CORRIGÉS")
    
    if not token:
        token = "<VOTRE_TOKEN_JWT>"
    
    curl_examples = f'''#!/bin/bash
# 🔧 EXEMPLES CURL CORRIGÉS - API AppGET
# =====================================

echo "🔑 1. AUTHENTIFICATION"
curl -X POST http://127.0.0.1:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "admin_test", "password": "admin123"}}'

echo ""
echo "📋 2. NOTIFICATIONS (avec token)"
curl -X GET http://127.0.0.1:8000/api/notifications/ \\
  -H "Authorization: Bearer {token}"

echo ""
echo "📅 3. EMPLOIS DU TEMPS"
curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ \\
  -H "Authorization: Bearer {token}"

echo ""
echo "🏛️ 4. DÉPARTEMENTS"
curl -X GET http://127.0.0.1:8000/api/core/departments/ \\
  -H "Authorization: Bearer {token}"

echo ""
echo "📚 5. PROGRAMMES"
curl -X GET http://127.0.0.1:8000/api/core/programs/ \\
  -H "Authorization: Bearer {token}"

echo ""
echo "👨‍🏫 6. ENSEIGNANTS"
curl -X GET http://127.0.0.1:8000/api/core/teachers/ \\
  -H "Authorization: Bearer {token}"

echo ""
echo "🏢 7. SALLES"
curl -X GET http://127.0.0.1:8000/api/core/rooms/ \\
  -H "Authorization: Bearer {token}"

echo ""
echo "⚡ 8. STATUS (sans token)"
curl -X GET http://127.0.0.1:8000/status/

echo ""
echo "✅ Tests terminés !"
'''
    
    with open("curl_examples_corrected.sh", 'w', encoding='utf-8') as f:
        f.write(curl_examples)
    
    print(f"✅ Exemples cURL corrigés sauvegardés dans curl_examples_corrected.sh")

def show_final_instructions():
    """Afficher les instructions finales"""
    print_header("INSTRUCTIONS FINALES")
    
    print("🎯 POUR RÉSOUDRE COMPLÈTEMENT LE PROBLÈME :")
    print()
    print("1. 🔄 REDÉMARRER LE SERVEUR DJANGO")
    print("   Ctrl+C pour arrêter, puis :")
    print("   python manage.py runserver")
    print()
    print("2. 🧪 TESTER L'AUTHENTIFICATION")
    print("   curl -X POST http://127.0.0.1:8000/api/auth/login/ \\")
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"username": "admin_test", "password": "admin123"}\'')
    print()
    print("3. 📝 UTILISER LE TOKEN OBTENU")
    print("   curl -X GET http://127.0.0.1:8000/api/notifications/ \\")
    print("     -H \"Authorization: Bearer <VOTRE_TOKEN>\"")
    print()
    print("🔑 COMPTES DISPONIBLES :")
    print("   👤 admin_test / admin123")
    print("   👤 teacher_test / teacher123") 
    print("   👤 student_test / student123")
    print()
    print("📁 FICHIERS UTILES :")
    print("   📄 curl_examples_corrected.sh - Exemples cURL corrigés")
    print("   📄 api_usage_examples.json - Exemples JSON")

def main():
    """Fonction principale"""
    print("🚀 CORRECTION DU PROBLÈME TESTSERVER")
    
    try:
        # Étape 1 : Corriger les ALLOWED_HOSTS
        if fix_allowed_hosts():
            print("⚠️  Vous devez redémarrer le serveur Django pour que les changements prennent effet")
        
        # Étape 2 : Tester avec le serveur réel
        token = test_with_real_server()
        
        # Étape 3 : Créer des exemples corrigés
        create_curl_examples_with_token(token)
        
        # Étape 4 : Instructions finales
        show_final_instructions()
        
        print("\n" + "="*60)
        print("✅ CORRECTION TERMINÉE !")
        print("💡 Redémarrez le serveur Django et testez à nouveau")
        
    except Exception as e:
        print(f"❌ Erreur générale : {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
