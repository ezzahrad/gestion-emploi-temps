@echo off
echo 🔧 Correction et test d'AppGET Frontend
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Nettoyage du cache...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist .vite rmdir /s /q .vite

echo [2/4] Installation des dépendances...
npm install

echo [3/4] Vérification de la configuration...
npm run type-check
if errorlevel 1 (
    echo [ERREUR] Problème de TypeScript détecté
    pause
    exit /b 1
)

echo [4/4] Démarrage du serveur de développement...
echo.
echo ✅ Configuration corrigée !
echo 🌐 Ouverture sur http://localhost:5173
echo.
npm run dev

pause