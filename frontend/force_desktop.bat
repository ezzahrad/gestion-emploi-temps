@echo off
title AppGET - FORCER INTERFACE DESKTOP
echo 🖥️  AppGET - INTERFACE DESKTOP FORCÉE
echo =====================================
echo.

cd /d "%~dp0"

echo 🔄 ÉTAPE 1: Arrêt du serveur en cours...
taskkill /f /im node.exe >nul 2>&1

echo 🧹 ÉTAPE 2: Nettoyage complet du cache...
if exist .vite rmdir /s /q .vite
if exist dist rmdir /s /q dist
if exist node_modules\.vite rmdir /s /q node_modules\.vite

echo 📝 ÉTAPE 3: Vérification des modifications...
echo    ✅ index.html - Écran de chargement desktop
echo    ✅ index.css - Classes CSS desktop forcées  
echo    ✅ Layout.tsx - Interface sidebar extensible
echo    ✅ App.tsx - Classes force-desktop appliquées

echo 🌐 ÉTAPE 4: Démarrage avec cache vidé...
set VITE_FORCE_OPTIMIZE=true

echo.
echo 🎯 INSTRUCTIONS IMPORTANTES :
echo    1. L'écran de chargement simule déjà l'interface desktop
echo    2. Sidebar à gauche avec logo AppGET
echo    3. Contenu principal à droite avec spinner
echo    4. Plus de design mobile centré
echo.
echo    Si l'interface reste mobile :
echo    - Appuyez sur Ctrl+Shift+R pour vider le cache
echo    - Testez en navigation privée
echo    - Vérifiez F12 > Console pour erreurs
echo.

timeout 3
start "" http://localhost:5173

echo 🚀 Lancement avec interface desktop forcée...
npm run dev