# Création des migrations pour authentication
python manage.py makemigrations authentication

# Création des migrations pour core
python manage.py makemigrations core

# Application des migrations de base
python manage.py migrate

echo "✅ Migrations de base créées avec succès!"
