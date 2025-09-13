@echo off
echo 🔍 DIAGNOSTIC INTERFACE DESKTOP AppGET
echo ====================================
echo.

cd /d "%~dp0"

echo [1/5] Vérification des fichiers critiques...
if not exist "src\index.css" (
    echo ❌ ERREUR: src\index.css manquant
    goto :error
) else (
    echo ✅ src\index.css trouvé
)

if not exist "src\components\Layout.tsx" (
    echo ❌ ERREUR: src\components\Layout.tsx manquant  
    goto :error
) else (
    echo ✅ src\components\Layout.tsx trouvé
)

if not exist "src\App.tsx" (
    echo ❌ ERREUR: src\App.tsx manquant
    goto :error
) else (
    echo ✅ src\App.tsx trouvé
)

echo [2/5] Vérification des classes CSS desktop...
findstr /C:"force-desktop" src\index.css >nul 2>&1
if errorlevel 1 (
    echo ❌ Classes desktop manquantes dans index.css
    goto :error
) else (
    echo ✅ Classes CSS desktop trouvées
)

echo [3/5] Vérification Layout desktop...
findstr /C:"desktop-layout" src\components\Layout.tsx >nul 2>&1
if errorlevel 1 (
    echo ❌ Layout desktop manquant
    goto :error
) else (
    echo ✅ Layout desktop configuré
)

echo [4/5] Vérification App configuration...  
findstr /C:"force-desktop" src\App.tsx >nul 2>&1
if errorlevel 1 (
    echo ❌ Configuration App manquante
    goto :error
) else (
    echo ✅ App configuré pour desktop
)

echo [5/5] Test de démarrage...
echo ✅ Tous les fichiers desktop sont présents !
echo.
echo 📋 LISTE DE VÉRIFICATION INTERFACE :
echo    ✓ L'interface doit utiliser toute la largeur
echo    ✓ Sidebar à gauche extensible/rétractable
echo    ✓ Topbar en haut avec recherche  
echo    ✓ Contenu principal sans limitation de largeur
echo    ✓ Plus de design mobile centré
echo.
echo 🎯 Si l'interface reste mobile après démarrage :
echo    1. Actualisez avec Ctrl+Shift+R
echo    2. Vérifiez F12 > Console pour erreurs
echo    3. Testez sur autre navigateur
echo.

echo Appuyez sur une touche pour démarrer l'application...
pause >nul

echo 🚀 Démarrage avec interface desktop forcée...
start "" http://localhost:5173
npm run dev

goto :end

:error
echo.
echo ❌ PROBLÈME DÉTECTÉ !
echo 📋 Actions recommandées :
echo    1. Vérifiez que tous les fichiers sont présents
echo    2. Relancez les scripts de correction
echo    3. Consultez DESKTOP_FIXED.md pour plus d'infos
echo.
pause
exit /b 1

:end
echo.
echo ✅ Diagnostic terminé avec succès !
pause