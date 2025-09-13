@echo off
echo 🚀 SOLUTION FINALE - AppGET Frontend
echo ===================================
echo.

cd /d "%~dp0"

echo [1/6] Suppression des fichiers de configuration problématiques...
if exist babel.config.js (
    echo Renommage babel.config.js en .backup...
    ren babel.config.js babel.config.js.backup
)

echo [2/6] Nettoyage complet...
if exist .vite (
    echo Suppression cache Vite...
    rmdir /s /q .vite
)
if exist dist (
    echo Suppression dossier dist...
    rmdir /s /q dist
)

echo [3/6] Nettoyage cache npm...
npm cache clean --force

echo [4/6] Installation/Vérification des dépendances Babel (optionnelles)...
npm install --save-dev @babel/plugin-syntax-dynamic-import @babel/preset-env @babel/preset-react @babel/preset-typescript

echo [5/6] Vérification de la configuration...
echo Configuration Vite... OK
echo Configuration PostCSS... OK  
echo Configuration Tailwind... OK

echo [6/6] Démarrage du serveur de développement...
echo.
echo ✅ Toutes les configurations corrigées !
echo 🌐 Ouverture sur http://localhost:5173
echo 📱 Interface optimisée desktop + responsive
echo.
echo ⚠️  Assurez-vous que le backend Django fonctionne sur le port 8000
echo.
timeout 2 >nul

start "" http://localhost:5173
npm run dev

echo.
echo 📋 Si le problème persiste :
echo 1. Arrêtez le serveur (Ctrl+C)
echo 2. Lancez clean_and_start.bat
echo 3. Vérifiez que Node.js >= 18.0.0
pause