#!/usr/bin/env python3
"""
🔧 DIAGNOSTIC DES PROBLÈMES API - AppGET
========================================

Script pour diagnostiquer et résoudre les erreurs API identifiées :
1. HTTP 403 Forbidden (authentification manquante)
2. HTTP 404 (URLs mal configurées)
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def test_api_endpoints():
    """Test des endpoints API principaux"""
    print_header("TEST DES ENDPOINTS API")
    
    client = APIClient()
    
    # URLs à tester
    urls_to_test = [
        '/api/auth/',
        '/api/core/',
        '/api/schedule/',
        '/api/notifications/',
        '/api/schedule/schedules/',
        '/status/',
    ]
    
    print("📍 Test des URLs sans authentification :")
    for url in urls_to_test:
        try:
            response = client.get(url)
            status_emoji = "✅" if response.status_code < 400 else "❌"
            print(f"  {status_emoji} {url} → {response.status_code}")
            if response.status_code == 403:
                print(f"      💡 Nécessite une authentification")
            elif response.status_code == 404:
                print(f"      💡 URL non trouvée - vérifier la configuration")
        except Exception as e:
            print(f"  ❌ {url} → Erreur: {e}")

def check_url_patterns():
    """Vérification des patterns d'URL"""
    print_header("ANALYSE DES PATTERNS D'URL")
    
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        print("📋 Patterns d'URL disponibles :")
        patterns = []
        
        def extract_patterns(urlpatterns, prefix=''):
            for pattern in urlpatterns:
                if hasattr(pattern, 'url_patterns'):
                    # C'est un include()
                    new_prefix = prefix + str(pattern.pattern)
                    extract_patterns(pattern.url_patterns, new_prefix)
                else:
                    # C'est un pattern normal
                    full_pattern = prefix + str(pattern.pattern)
                    patterns.append(full_pattern)
        
        extract_patterns(resolver.url_patterns)
        
        # Filtrer les patterns API
        api_patterns = [p for p in patterns if 'api' in p.lower()]
        
        for pattern in sorted(api_patterns):
            print(f"  📌 {pattern}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des URLs : {e}")

def check_authentication_config():
    """Vérification de la configuration d'authentification"""
    print_header("CONFIGURATION D'AUTHENTIFICATION")
    
    # REST Framework settings
    rf_settings = getattr(settings, 'REST_FRAMEWORK', {})
    
    print("🔐 Configuration REST Framework :")
    auth_classes = rf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])
    perm_classes = rf_settings.get('DEFAULT_PERMISSION_CLASSES', [])
    
    print(f"  📋 Classes d'authentification :")
    for auth_class in auth_classes:
        print(f"    • {auth_class}")
    
    print(f"  📋 Classes de permissions :")
    for perm_class in perm_classes:
        print(f"    • {perm_class}")
    
    if 'rest_framework.permissions.IsAuthenticated' in perm_classes:
        print(f"  ⚠️  TOUTES les API nécessitent une authentification par défaut")
        print(f"      C'est pourquoi vous avez l'erreur 403 Forbidden")

def create_test_user():
    """Création d'un utilisateur de test"""
    print_header("CRÉATION UTILISATEUR DE TEST")
    
    try:
        # Vérifier si un utilisateur de test existe
        try:
            user = User.objects.get(username='test_api')
            print("✅ Utilisateur de test existe déjà")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='test_api',
                email='test@appget.com',
                password='testpass123',
                first_name='Test',
                last_name='API'
            )
            print("✅ Utilisateur de test créé")
        
        print(f"  👤 Username: {user.username}")
        print(f"  📧 Email: {user.email}")
        print(f"  🔑 Password: testpass123")
        
        return user
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur : {e}")
        return None

def test_with_authentication():
    """Test des API avec authentification"""
    print_header("TEST AVEC AUTHENTIFICATION")
    
    # Créer un utilisateur de test
    user = create_test_user()
    if not user:
        return
    
    client = APIClient()
    
    # Test de connexion
    print("🔑 Test d'authentification :")
    login_data = {
        'username': 'test_api',
        'password': 'testpass123'
    }
    
    try:
        response = client.post('/api/auth/login/', login_data)
        print(f"  📍 POST /api/auth/login/ → {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'access' in data:
                token = data['access']
                print(f"  ✅ Token JWT reçu")
                
                # Tester les API avec le token
                client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                
                print(f"\n📋 Test des API avec authentification :")
                test_urls = [
                    '/api/notifications/',
                    '/api/schedule/schedules/',
                    '/api/core/',
                ]
                
                for url in test_urls:
                    response = client.get(url)
                    status_emoji = "✅" if response.status_code < 400 else "❌"
                    print(f"  {status_emoji} {url} → {response.status_code}")
            else:
                print(f"  ❌ Pas de token dans la réponse")
        else:
            print(f"  ❌ Échec de l'authentification")
            print(f"      Réponse: {response.content}")
            
    except Exception as e:
        print(f"  ❌ Erreur lors du test d'authentification : {e}")

def show_solutions():
    """Affichage des solutions"""
    print_header("SOLUTIONS RECOMMANDÉES")
    
    print("🎯 PROBLÈME 1 : HTTP 403 Forbidden (Notifications)")
    print("   📝 Cause : Authentification JWT manquante")
    print("   💡 Solution : Inclure le token JWT dans les headers")
    print("   📋 Headers requis :")
    print("      Authorization: Bearer <votre_token_jwt>")
    print()
    
    print("🎯 PROBLÈME 2 : HTTP 404 (Schedule)")
    print("   📝 Cause : URL incorrecte")
    print("   💡 Solution : Utiliser les bonnes URLs")
    print("   📋 URLs correctes :")
    print("      ❌ /api/schedule/")
    print("      ✅ /api/schedule/schedules/")
    print("      ✅ /api/schedule/absences/")
    print("      ✅ /api/schedule/makeup-sessions/")
    print()
    
    print("🔧 ACTIONS À EFFECTUER :")
    print("   1. 🔑 Se connecter via /api/auth/login/ pour obtenir un token")
    print("   2. 📤 Inclure 'Authorization: Bearer <token>' dans tous les appels API")
    print("   3. 🔗 Utiliser les URLs complètes avec 'schedules', 'absences', etc.")
    print("   4. 🧪 Tester avec l'utilisateur créé (test_api / testpass123)")

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DU DIAGNOSTIC API AppGET")
    
    try:
        check_url_patterns()
        check_authentication_config()
        test_api_endpoints()
        test_with_authentication()
        show_solutions()
        
        print_header("DIAGNOSTIC TERMINÉ")
        print("✅ Le diagnostic est maintenant complet !")
        print("📖 Consultez les solutions ci-dessus pour résoudre les problèmes.")
        
    except Exception as e:
        print(f"❌ Erreur générale : {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
