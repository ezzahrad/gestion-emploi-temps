@echo off
title AppGET - Interface Desktop Optimisée
echo 🖥️  AppGET - INTERFACE DESKTOP OPTIMISÉE
echo =========================================
echo.

cd /d "%~dp0"

echo ✅ CORRECTIONS APPLIQUÉES :
echo.
echo 📱 ❌ Interface mobile étroite SUPPRIMÉE
echo 🖥️  ✅ Interface desktop FORCÉE (largeur complète)
echo 📐 ✅ Sidebar extensible 320px ↔ 64px
echo 🎨 ✅ Layout responsive optimisé
echo 🔧 ✅ Classes CSS desktop forcées
echo.
echo 🔄 Démarrage de l'interface desktop...
timeout 2 >nul

echo 🌐 Ouverture automatique du navigateur...
start "" http://localhost:5173

echo.
echo 📋 VÉRIFICATIONS À EFFECTUER :
echo    ✓ L'interface utilise toute la largeur de l'écran
echo    ✓ Sidebar à gauche extensible/rétractable  
echo    ✓ Topbar en haut avec recherche étendue
echo    ✓ Contenu principal utilise l'espace restant
echo    ✓ Plus de largeur maximale contrainte
echo.
echo 🎯 Si l'interface reste mobile :
echo    1. Actualisez la page (F5)
echo    2. Videz le cache (Ctrl+Shift+R)  
echo    3. Vérifiez les outils de développement (F12)
echo.

npm run dev