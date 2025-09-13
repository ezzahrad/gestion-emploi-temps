@echo off
echo ========================================
echo RESOLUTION DES MIGRATIONS - appGET
echo ========================================

echo.
echo Phase 1: Creation des migrations de base
echo ----------------------------------------

echo Etape 1: Creation des migrations authentication...
python manage.py makemigrations authentication
if %errorlevel% neq 0 (
    echo ERREUR: Echec creation migrations authentication
    pause
    exit /b 1
)

echo Etape 2: Creation des migrations core...
python manage.py makemigrations core
if %errorlevel% neq 0 (
    echo ERREUR: Echec creation migrations core
    pause
    exit /b 1
)

echo Etape 3: Application des migrations de base...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERREUR: Echec application migrations de base
    pause
    exit /b 1
)

echo.
echo ✅ Phase 1 terminee avec succes!
echo.

echo Phase 2: Restauration du modele complet
echo ----------------------------------------

echo Etape 4: Copie du modele complet...
copy core\models_complete.py core\models.py
if %errorlevel% neq 0 (
    echo ERREUR: Echec copie du modele complet
    pause
    exit /b 1
)

echo Etape 5: Creation migration pour champs head...
python manage.py makemigrations core
if %errorlevel% neq 0 (
    echo ERREUR: Echec creation migration champs head
    pause
    exit /b 1
)

echo Etape 6: Creation migrations schedule...
python manage.py makemigrations schedule
if %errorlevel% neq 0 (
    echo ERREUR: Echec creation migrations schedule
    pause
    exit /b 1
)

echo Etape 7: Creation migrations notifications...
python manage.py makemigrations notifications
if %errorlevel% neq 0 (
    echo ERREUR: Echec creation migrations notifications
    pause
    exit /b 1
)

echo Etape 8: Application de toutes les migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERREUR: Echec application migrations finales
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅✅✅ SUCCES COMPLET! ✅✅✅
echo Toutes les migrations ont ete creees!
echo ========================================

echo.
echo Verification finale...
python manage.py showmigrations

echo.
echo Appuyez sur une touche pour continuer...
pause
