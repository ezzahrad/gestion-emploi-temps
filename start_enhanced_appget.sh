#!/bin/bash

# Script de démarrage rapide pour les nouvelles fonctionnalités AppGET
# Usage: ./start_enhanced_appget.sh

echo "🚀 DÉMARRAGE APPGET - NOUVELLES FONCTIONNALITÉS"
echo "=================================================="

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

# Vérifier Python
if ! command -v python &> /dev/null; then
    echo "❌ Python non trouvé. Veuillez installer Python 3.8+"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js non trouvé. Veuillez installer Node.js 18+"
    exit 1
fi

echo "✅ Prérequis OK"

# Démarrer le backend
echo ""
echo "🔧 Démarrage du backend Django..."
cd backend

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate || venv\Scripts\activate
fi

# Installer les dépendances si nécessaire
if [ ! -f ".dependencies_installed" ]; then
    echo "Installation des dépendances Python..."
    pip install -r requirements.txt
    pip install reportlab Pillow
    touch .dependencies_installed
fi

# Exécuter les migrations si nécessaire
echo "Application des migrations..."
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur si nécessaire
echo "Vérification du superutilisateur..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@appget.local', 'admin123', first_name='Admin', last_name='AppGET')
    print('✅ Superutilisateur créé (admin/admin123)')
else:
    print('✅ Superutilisateur existant')
"

# Démarrer le serveur Django en arrière-plan
echo "Démarrage du serveur Django..."
python manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!

cd ..

# Démarrer le frontend
echo ""
echo "🔧 Démarrage du frontend React..."
cd frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances Node.js..."
    npm install
fi

# Démarrer le serveur de développement
echo "Démarrage du serveur React..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Attendre que les serveurs démarrent
echo ""
echo "⏳ Démarrage des serveurs..."
sleep 5

# Vérifier que les serveurs fonctionnent
echo ""
echo "🔍 Vérification des serveurs..."

if curl -s http://127.0.0.1:8000/status/ > /dev/null; then
    echo "✅ Backend Django : http://127.0.0.1:8000"
else
    echo "❌ Backend Django non accessible"
fi

if curl -s http://localhost:5173/ > /dev/null; then
    echo "✅ Frontend React : http://localhost:5173"
else
    echo "❌ Frontend React non accessible"
fi

echo ""
echo "🎉 APPGET DÉMARRÉ AVEC SUCCÈS !"
echo "================================"
echo ""
echo "📱 Application : http://localhost:5173"
echo "🔧 Admin Django : http://127.0.0.1:8000/admin"
echo "📊 API Status : http://127.0.0.1:8000/status/"
echo ""
echo "👤 Compte admin :"
echo "   Email : admin@appget.local"
echo "   Mot de passe : admin123"
echo ""
echo "🆕 NOUVELLES FONCTIONNALITÉS DISPONIBLES :"
echo "   ✅ Gestion des notes et évaluations"
echo "   ✅ Gestion des absences et rattrapages"
echo "   ✅ Export PDF avancé"
echo "   ✅ Notifications temps réel"
echo ""
echo "📚 Documentation : ./NOUVELLES_FONCTIONNALITES.md"
echo ""
echo "Pour arrêter les serveurs : Ctrl+C"
echo "PIDs : Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Serveurs arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Attendre indéfiniment
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"
while true; do
    sleep 1
done
