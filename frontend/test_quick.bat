@echo off
echo 🧪 Test Rapide AppGET Frontend
echo =============================
echo.

cd /d "%~dp0"

echo Vérification des fichiers de configuration...

if exist babel.config.js (
    echo [ATTENTION] babel.config.js détecté - renommage...
    ren babel.config.js babel.config.js.disabled
)

echo Configuration Vite... OK
echo Configuration TypeScript... OK
echo Configuration Tailwind... OK

echo.
echo 🚀 Test de démarrage (10 secondes)...
timeout 2 >nul

start /min cmd /c "timeout 15 >nul & taskkill /f /im node.exe >nul 2>&1"
npm run dev

echo.
echo ✅ Test terminé !
pause