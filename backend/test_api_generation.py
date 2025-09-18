"""
Test rapide de l'API de génération avec les bonnes permissions
"""
import requests
import json

def test_login_and_generate():
    """Tester la connexion et la génération d'emploi du temps"""
    print("🧪 TEST COMPLET DE L'API")
    print("=" * 25)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test avec différents utilisateurs
    test_users = [
        {'email': 'souadibaaz@gmail.com', 'password': 'admin123'},
        {'email': 'admin.test@appget.local', 'password': 'admin123'},
        {'email': 'admin@appget.local', 'password': 'admin123'},
    ]
    
    for user_data in test_users:
        print(f"\n👤 Test avec {user_data['email']}:")
        
        try:
            # 1. Connexion
            login_response = requests.post(
                f"{base_url}/api/auth/login/",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   📥 Connexion: {login_response.status_code}")
            
            if login_response.status_code != 200:
                print(f"   ❌ Échec de connexion: {login_response.text}")
                continue
            
            login_data = login_response.json()
            token = login_data.get('token')
            user_info = login_data.get('user', {})
            
            print(f"   ✅ Token obtenu: {token[:20] if token else 'Aucun'}...")
            print(f"   🎭 Rôle: {user_info.get('role', 'Inconnu')}")
            
            if not token:
                print(f"   ❌ Pas de token")
                continue
            
            # 2. Test de génération
            generation_data = {
                'program_ids': [22, 23],  # IDs existants selon le diagnostic
                'start_date': '2025-09-23',
                'end_date': '2025-10-23',
                'include_weekends': False,
                'max_sessions_per_day': 6
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            generation_response = requests.post(
                f"{base_url}/api/generate/timetable/",
                json=generation_data,
                headers=headers
            )
            
            print(f"   📊 Génération: {generation_response.status_code}")
            
            if generation_response.status_code == 200:
                result = generation_response.json()
                print(f"   🎉 SUCCÈS!")
                if 'stats' in result:
                    stats = result['stats']
                    print(f"   📈 Séances créées: {stats.get('schedules_created', 0)}")
                    print(f"   🔄 Conflits: {stats.get('conflicts_detected', 0)}")
                return True
            else:
                print(f"   ❌ Erreur: {generation_response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return False

def quick_api_test():
    """Test simple de l'API"""
    print("🚀 TEST RAPIDE API")
    print("=" * 18)
    
    try:
        # Test de base - status de l'API
        response = requests.get("http://127.0.0.1:8000/status/")
        print(f"📡 API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API active: {data.get('status', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ API non accessible: {e}")
        return False

if __name__ == "__main__":
    print("🔬 TEST COMPLET - GÉNÉRATION EMPLOI DU TEMPS")
    print("=" * 45)
    
    # Test 1: API accessible
    api_ok = quick_api_test()
    
    if api_ok:
        # Test 2: Connexion et génération
        generation_ok = test_login_and_generate()
        
        if generation_ok:
            print(f"\n🎉 TOUS LES TESTS RÉUSSIS!")
            print(f"La génération d'emploi du temps fonctionne parfaitement.")
        else:
            print(f"\n💡 Essayez les solutions suivantes:")
            print(f"1. Exécutez d'abord: python fix_permissions.py")
            print(f"2. Redémarrez le serveur Django")
            print(f"3. Vérifiez les mots de passe des utilisateurs")
    else:
        print(f"\n❌ Serveur Django non accessible")
        print(f"Assurez-vous qu'il tourne sur http://127.0.0.1:8000")
