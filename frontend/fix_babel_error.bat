@echo off
echo 🛠️ Correction urgente AppGET Frontend
echo ===================================
echo.

cd /d "%~dp0"

echo [1/5] Arrêt des processus Vite...
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 >nul

echo [2/5] Nettoyage complet...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist .vite rmdir /s /q .vite
if exist dist rmdir /s /q dist

echo [3/5] Installation des dépendances...
npm install

echo [4/5] Installation des plugins Babel manquants...
npm install --save-dev @babel/plugin-syntax-dynamic-import @babel/plugin-syntax-jsx

echo [5/5] Démarrage...
echo.
echo ✅ Configuration Babel corrigée !
echo 🌐 Ouverture sur http://localhost:5173
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.
npm run dev

pause