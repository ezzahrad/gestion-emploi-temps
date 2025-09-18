#!/bin/bash
set -e

echo "🚀 Démarrage AppGET - Nouvelles Fonctionnalités"

# Attendre que la base de données soit disponible
echo "⏳ Attente de la base de données..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ Base de données accessible"

# Attendre que Redis soit disponible
echo "⏳ Attente de Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "✅ Redis accessible"

# Exécuter les migrations
echo "🔧 Application des migrations..."
python manage.py makemigrations
python manage.py makemigrations notifications
python manage.py makemigrations grades
python manage.py makemigrations absences
python manage.py makemigrations pdf_export
python manage.py migrate

# Créer un superutilisateur si nécessaire
echo "👤 Création du superutilisateur..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@appget.docker',
        password='admin123',
        first_name='Admin',
        last_name='Docker'
    )
    print('✅ Superutilisateur créé (admin/admin123)')
else:
    print('✅ Superutilisateur existant')
"

# Créer les données de base
echo "📊 Création des données de base..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

# Échelle de notation
try:
    from grades.models import GradeScale
    if not GradeScale.objects.filter(is_default=True).exists():
        GradeScale.objects.create(
            name='Échelle Française',
            is_default=True,
            a_plus_min=18.0,
            a_min=16.0,
            b_plus_min=14.0,
            b_min=12.0,
            c_plus_min=10.0,
            c_min=8.0,
            d_plus_min=6.0,
            d_min=4.0
        )
        print('✅ Échelle de notation créée')
except ImportError:
    print('⚠️  Module grades non disponible')

# Politique d'absence
try:
    from absences.models import AbsencePolicy
    if not AbsencePolicy.objects.filter(is_default=True).exists():
        AbsencePolicy.objects.create(
            name='Politique Standard Docker',
            is_default=True,
            max_unjustified_absences=3,
            max_total_absences_percentage=25.0,
            justification_deadline_hours=48,
            makeup_request_deadline_days=7
        )
        print('✅ Politique d'\''absence créée')
except ImportError:
    print('⚠️  Module absences non disponible')

# Paramètres PDF
try:
    from pdf_export.models import PDFExportSettings
    if not PDFExportSettings.objects.exists():
        PDFExportSettings.objects.create(
            output_directory='pdf_exports/',
            temp_directory='pdf_temp/',
            max_file_size_mb=50,
            max_pages_per_document=500,
            max_concurrent_jobs=5,
            job_retention_days=7,
            image_quality=85,
            compression_level=6
        )
        print('✅ Paramètres PDF créés')
except ImportError:
    print('⚠️  Module pdf_export non disponible')
"

# Collecter les fichiers statiques
echo "📁 Collection des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🎉 Initialisation terminée !"

# Exécuter la commande passée en argument
exec "$@"
