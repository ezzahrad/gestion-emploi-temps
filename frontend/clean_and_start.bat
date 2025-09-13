@echo off
echo 🔧 Nettoyage Complet Frontend AppGET
echo ==================================
echo.

cd /d "%~dp0"

echo [1/5] Nettoyage des caches et modules...
if exist node_modules (
    echo Suppression node_modules...
    rmdir /s /q node_modules
)
if exist package-lock.json (
    echo Suppression package-lock.json...
    del package-lock.json
)
if exist .vite (
    echo Suppression cache Vite...
    rmdir /s /q .vite
)
if exist dist (
    echo Suppression dist...
    rmdir /s /q dist
)

echo [2/5] Vérification Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js non installé !
    echo Téléchargez depuis https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js trouvé: 
node --version

echo [3/5] Installation propre des dépendances...
npm cache clean --force
npm install

echo [4/5] Vérification TypeScript...
npm run type-check
if errorlevel 1 (
    echo [ATTENTION] Erreurs TypeScript détectées, mais on continue...
)

echo [5/5] Test de démarrage...
echo.
echo ✅ Configuration nettoyée !
echo 🌐 Démarrage sur http://localhost:5173
echo ⚠️  Assurez-vous que le backend Django tourne sur le port 8000
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
timeout 3 >nul

npm run dev

pause