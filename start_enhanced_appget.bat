@echo off
REM Script de démarrage rapide pour les nouvelles fonctionnalités AppGET (Windows)
REM Usage: start_enhanced_appget.bat

echo 🚀 DÉMARRAGE APPGET - NOUVELLES FONCTIONNALITÉS
echo ==================================================

REM Vérifier les prérequis
echo 🔍 Vérification des prérequis...

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé. Veuillez installer Python 3.8+
    pause
    exit /b 1
)

REM Vérifier Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js non trouvé. Veuillez installer Node.js 18+
    pause
    exit /b 1
)

echo ✅ Prérequis OK

REM Démarrer le backend
echo.
echo 🔧 Démarrage du backend Django...
cd backend

REM Activer l'environnement virtuel s'il existe
if exist "venv\Scripts\activate.bat" (
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
)

REM Installer les dépendances si nécessaire
if not exist ".dependencies_installed" (
    echo Installation des dépendances Python...
    pip install -r requirements.txt
    pip install reportlab Pillow
    echo. > .dependencies_installed
)

REM Exécuter les migrations si nécessaire
echo Application des migrations...
python manage.py makemigrations
python manage.py migrate

REM Créer un superutilisateur si nécessaire
echo Vérification du superutilisateur...
python -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings'); django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@appget.local', 'admin123', first_name='Admin', last_name='AppGET') if not User.objects.filter(is_superuser=True).exists() else None; print('✅ Superutilisateur créé (admin/admin123)' if not User.objects.filter(username='admin').exists() else '✅ Superutilisateur existant')"

REM Démarrer le serveur Django en arrière-plan
echo Démarrage du serveur Django...
start "AppGET Backend" cmd /c "python manage.py runserver 127.0.0.1:8000"

cd ..

REM Démarrer le frontend
echo.
echo 🔧 Démarrage du frontend React...
cd frontend

REM Installer les dépendances si nécessaire
if not exist "node_modules" (
    echo Installation des dépendances Node.js...
    npm install
)

REM Démarrer le serveur de développement
echo Démarrage du serveur React...
start "AppGET Frontend" cmd /c "npm run dev"

cd ..

REM Attendre que les serveurs démarrent
echo.
echo ⏳ Démarrage des serveurs...
timeout /t 5 /nobreak >nul

REM Informations finales
echo.
echo 🎉 APPGET DÉMARRÉ AVEC SUCCÈS !
echo ================================
echo.
echo 📱 Application : http://localhost:5173
echo 🔧 Admin Django : http://127.0.0.1:8000/admin
echo 📊 API Status : http://127.0.0.1:8000/status/
echo.
echo 👤 Compte admin :
echo    Email : admin@appget.local
echo    Mot de passe : admin123
echo.
echo 🆕 NOUVELLES FONCTIONNALITÉS DISPONIBLES :
echo    ✅ Gestion des notes et évaluations
echo    ✅ Gestion des absences et rattrapages
echo    ✅ Export PDF avancé
echo    ✅ Notifications temps réel
echo.
echo 📚 Documentation : ./NOUVELLES_FONCTIONNALITES.md
echo.
echo Pour arrêter : Fermez les fenêtres des serveurs
echo.

REM Ouvrir automatiquement l'application dans le navigateur
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo 🌐 Application ouverte dans le navigateur
echo.
pause
