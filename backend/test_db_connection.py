# test_db_connection.py - Tester la connexion à PostgreSQL
import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from django.db import connection
from django.core.management.color import no_style

def test_database_connection():
    """Tester la connexion à la base de données"""
    print("🔍 Test de connexion à la base de données...")
    print(f"Base: {settings.DATABASES['default']['NAME']}")
    print(f"Utilisateur: {settings.DATABASES['default']['USER']}")
    print(f"Host: {settings.DATABASES['default']['HOST']}")
    print(f"Port: {settings.DATABASES['default']['PORT']}")
    
    try:
        # Tenter une connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connexion réussie!")
            print(f"Version PostgreSQL: {version[0]}")
            
            # Tester les permissions
            cursor.execute("SELECT current_user, current_database();")
            user_db = cursor.fetchone()
            print(f"Utilisateur connecté: {user_db[0]}")
            print(f"Base de données: {user_db[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_database_permissions():
    """Tester les permissions de création de table"""
    print("\n🔧 Test des permissions...")
    
    try:
        with connection.cursor() as cursor:
            # Tester la création d'une table de test
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_permissions (
                    id SERIAL PRIMARY KEY,
                    test_field VARCHAR(50)
                );
            """)
            print("✅ Permission CREATE TABLE: OK")
            
            # Tester l'insertion
            cursor.execute("INSERT INTO test_permissions (test_field) VALUES ('test');")
            print("✅ Permission INSERT: OK")
            
            # Tester la sélection
            cursor.execute("SELECT * FROM test_permissions;")
            result = cursor.fetchall()
            print("✅ Permission SELECT: OK")
            
            # Nettoyer
            cursor.execute("DROP TABLE test_permissions;")
            print("✅ Permission DROP TABLE: OK")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de permissions: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TEST DE CONNEXION DATABASE APPGET")
    print("=" * 50)
    
    if test_database_connection():
        test_database_permissions()
        print("\n🎉 Tous les tests sont passés!")
        print("Vous pouvez maintenant exécuter: python manage.py migrate")
    else:
        print("\n❌ Problème de connexion détecté")
        print("Vérifiez la configuration de la base de données")
