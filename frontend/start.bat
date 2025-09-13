@echo off
title AppGET - Démarrage Rapide
echo 🚀 AppGET - DÉMARRAGE RAPIDE
echo ==========================
echo.

cd /d "%~dp0"

REM Vérification rapide
if not exist package.json (
    echo [ERREUR] Pas dans le bon dossier !
    pause
    exit /b 1
)

echo ✅ Configuration nettoyée : babel.config.js supprimé
echo ✅ Vite.config.ts simplifié  
echo ✅ Cache Vite propre
echo.
echo 🌐 Ouverture de http://localhost:5173
echo 🔗 Backend attendu sur http://127.0.0.1:8000
echo.
echo Appuyez sur Ctrl+C pour arrêter...
timeout 2 >nul

npm run dev