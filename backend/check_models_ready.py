# check_models_ready.py - Vérifier que les modèles Django sont prêts
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')

try:
    django.setup()
    print("✅ Django configuré avec succès")
except Exception as e:
    print(f"❌ Erreur configuration Django: {e}")
    exit(1)

def check_models():
    """Vérifier que tous les modèles nécessaires sont disponibles"""
    print("🔍 Vérification des modèles Django...")
    
    try:
        # Importer les modèles
        from authentication.models import User
        print("✅ Model User importé")
        
        from core.models import Department, Program, Room, Subject, Teacher, Student
        print("✅ Models Core importés")
        
        from schedule.models import Schedule
        print("✅ Model Schedule importé")
        
        # Vérifier les tables en base
        print("\n📊 Vérification des tables en base de données:")
        
        models_to_check = [
            (User, "Utilisateurs"),
            (Department, "Départements"), 
            (Program, "Programmes"),
            (Room, "Salles"),
            (Subject, "Matières"),
            (Teacher, "Enseignants"),
            (Student, "Étudiants"),
            (Schedule, "Emplois du temps")
        ]
        
        for model, name in models_to_check:
            try:
                count = model.objects.count()
                print(f"✅ {name}: {count} enregistrement(s)")
            except Exception as e:
                print(f"❌ {name}: Erreur - {e}")
                
        print("\n🎉 Modèles prêts pour la création de données!")
        print("\n🚀 Vous pouvez maintenant exécuter:")
        print("   - python create_quick_test_users.py (test rapide)")
        print("   - python create_sample_database.py (base complète)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifier que les migrations sont appliquées:")
        print("   python manage.py migrate")
        print("2. Vérifier la structure des modèles")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def check_admin_user():
    """Vérifier s'il y a déjà un utilisateur admin"""
    try:
        from authentication.models import User
        admin_count = User.objects.filter(role='admin').count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        
        print(f"\n👑 Administrateurs existants: {admin_count}")
        print(f"🔑 Superusers existants: {superuser_count}")
        
        if admin_count > 0:
            print("\nℹ️  Vous avez déjà des administrateurs.")
            print("   Les scripts de création préserveront les comptes admin existants.")
            
        return True
        
    except Exception as e:
        print(f"❌ Impossible de vérifier les admins: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VÉRIFICATION PRÉALABLE DES MODÈLES DJANGO")
    print("=" * 60)
    
    if check_models():
        check_admin_user()
        print("\n✅ Système prêt pour la création de données exemplaires!")
    else:
        print("\n❌ Problèmes détectés. Corrigez avant de continuer.")
