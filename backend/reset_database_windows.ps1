# reset_database_windows.ps1 - Script PowerShell pour réinitialiser la DB sur Windows
param(
    [switch]$Confirm = $false
)

Write-Host "🚀 RÉINITIALISATION DE LA BASE DE DONNÉES APPGET (Windows)" -ForegroundColor Cyan
Write-Host "=" * 60

# Vérification de confirmation
if (-not $Confirm) {
    $response = Read-Host "⚠️  ATTENTION: Cette opération va SUPPRIMER toutes les données existantes!`nÊtes-vous sûr de vouloir continuer? (tapez 'OUI' pour confirmer)"
    if ($response -ne 'OUI') {
        Write-Host "❌ Opération annulée" -ForegroundColor Red
        exit
    }
}

try {
    Write-Host "`n📋 ÉTAPE 1: Suppression de l'ancienne base SQLite" -ForegroundColor Yellow
    if (Test-Path "db.sqlite3") {
        Remove-Item "db.sqlite3" -Force
        Write-Host "✅ db.sqlite3 supprimé" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Aucun fichier db.sqlite3 trouvé" -ForegroundColor Blue
    }

    Write-Host "`n📋 ÉTAPE 2: Nettoyage des migrations" -ForegroundColor Yellow
    
    # Trouver tous les dossiers migrations
    $migrationDirs = Get-ChildItem -Path . -Recurse -Directory -Name "migrations"
    
    foreach ($dir in $migrationDirs) {
        $fullPath = Join-Path (Get-Location) $dir
        Write-Host "🧹 Nettoyage de $fullPath" -ForegroundColor Gray
        
        # Supprimer tous les .py sauf __init__.py
        Get-ChildItem -Path $fullPath -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
        Get-ChildItem -Path $fullPath -Filter "*.pyc" | Remove-Item -Force
        
        # S'assurer que __init__.py existe
        $initFile = Join-Path $fullPath "__init__.py"
        if (-not (Test-Path $initFile)) {
            New-Item -Path $initFile -ItemType File -Force | Out-Null
        }
    }
    Write-Host "✅ Migrations nettoyées" -ForegroundColor Green

    Write-Host "`n📋 ÉTAPE 3: Création des nouvelles migrations" -ForegroundColor Yellow
    $result = python manage.py makemigrations 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations créées avec succès" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "⚠️  Première tentative échouée, essai avec --empty" -ForegroundColor Yellow
        python manage.py makemigrations core --empty --name initial_setup
        python manage.py makemigrations core
        Write-Host "✅ Migrations créées avec succès (deuxième tentative)" -ForegroundColor Green
    }

    Write-Host "`n📋 ÉTAPE 4: Application des migrations" -ForegroundColor Yellow
    python manage.py migrate
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations appliquées avec succès" -ForegroundColor Green
    } else {
        throw "Erreur lors de l'application des migrations"
    }

    Write-Host "`n📋 ÉTAPE 5: Création du superutilisateur" -ForegroundColor Yellow
    Write-Host "Veuillez entrer les informations pour le superutilisateur:" -ForegroundColor Cyan
    python manage.py createsuperuser

    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
    Write-Host "🎉 RÉINITIALISATION TERMINÉE AVEC SUCCÈS!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "✅ Nouvelle base de données créée" -ForegroundColor Green
    Write-Host "✅ Tables créées selon la nouvelle structure" -ForegroundColor Green
    Write-Host "✅ Prêt à démarrer l'application" -ForegroundColor Green
    Write-Host "`nPour démarrer le serveur:" -ForegroundColor Cyan
    Write-Host "  python manage.py runserver" -ForegroundColor White

} catch {
    Write-Host "`n❌ ERREUR FATALE: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Vérifiez que Django est bien installé et configuré" -ForegroundColor Yellow
}
