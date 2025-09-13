Write-Host "========================================" -ForegroundColor Green
Write-Host "RESOLUTION MIGRATIONS - appGET" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nPhase 1: Creation des migrations de base" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

Write-Host "`nEtape 1: Creation des migrations authentication..." -ForegroundColor Cyan
$result1 = python manage.py makemigrations authentication
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec creation migrations authentication" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`nEtape 2: Creation des migrations core..." -ForegroundColor Cyan
$result2 = python manage.py makemigrations core
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec creation migrations core" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`nEtape 3: Application des migrations de base..." -ForegroundColor Cyan
$result3 = python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec application migrations de base" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`n Phase 1 terminee avec succes!" -ForegroundColor Green

Write-Host "`nPhase 2: Restauration du modele complet" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

Write-Host "`nEtape 4: Copie du modele complet..." -ForegroundColor Cyan
Copy-Item "core\models_complete.py" "core\models.py" -Force
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec copie du modele complet" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`nEtape 5: Creation migration pour champs head..." -ForegroundColor Cyan
$result5 = python manage.py makemigrations core
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec creation migration champs head" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`nEtape 6: Creation migrations schedule..." -ForegroundColor Cyan
$result6 = python manage.py makemigrations schedule
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec creation migrations schedule" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`nEtape 7: Creation migrations notifications..." -ForegroundColor Cyan
$result7 = python manage.py makemigrations notifications
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec creation migrations notifications" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`nEtape 8: Application de toutes les migrations..." -ForegroundColor Cyan
$result8 = python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Echec application migrations finales" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " SUCCES COMPLET! " -ForegroundColor Green
Write-Host "Toutes les migrations ont ete creees!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nVerification finale..." -ForegroundColor Cyan
python manage.py showmigrations

Write-Host "`nProchaines etapes:" -ForegroundColor Yellow
Write-Host "1. python manage.py createsuperuser" -ForegroundColor White
Write-Host "2. python manage.py runserver" -ForegroundColor White
Write-Host "3. http://127.0.0.1:8000/admin/" -ForegroundColor White

Read-Host "`nAppuyez sur Entree pour continuer..."
