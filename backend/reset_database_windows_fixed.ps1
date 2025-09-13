# reset_database_windows.ps1 - Script PowerShell corrige pour reinitialiser la DB sur Windows
param(
    [switch]$Confirm = $false
)

Write-Host "🚀 REINITIALISATION DE LA BASE DE DONNEES APPGET (Windows)" -ForegroundColor Cyan
Write-Host ("=" * 60)

# Verification de confirmation
if (-not $Confirm) {
    $response = Read-Host "⚠️  ATTENTION: Cette operation va SUPPRIMER toutes les donnees existantes!`nEtes-vous sur de vouloir continuer? (tapez 'OUI' pour confirmer)"
    if ($response -ne 'OUI') {
        Write-Host "❌ Operation annulee" -ForegroundColor Red
        exit
    }
}

try {
    Write-Host "`n📋 ETAPE 1: Suppression de l'ancienne base SQLite" -ForegroundColor Yellow
    if (Test-Path "db.sqlite3") {
        Remove-Item "db.sqlite3" -Force
        Write-Host "✅ db.sqlite3 supprime" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Aucun fichier db.sqlite3 trouve" -ForegroundColor Blue
    }

    Write-Host "`n📋 ETAPE 2: Nettoyage des migrations" -ForegroundColor Yellow
    
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
    Write-Host "✅ Migrations nettoyees" -ForegroundColor Green

    Write-Host "`n📋 ETAPE 3: Creation des nouvelles migrations" -ForegroundColor Yellow
    
    # Créer d'abord les migrations pour authentication (qui semble être prioritaire)
    Write-Host "Création des migrations pour authentication..." -ForegroundColor Gray
    python manage.py makemigrations authentication
    
    # Puis pour core
    Write-Host "Création des migrations pour core..." -ForegroundColor Gray
    python manage.py makemigrations core
    
    # Puis pour les autres apps
    Write-Host "Création des migrations pour les autres apps..." -ForegroundColor Gray
    python manage.py makemigrations
    
    Write-Host "✅ Migrations creees avec succes" -ForegroundColor Green

    Write-Host "`n📋 ETAPE 4: Application des migrations" -ForegroundColor Yellow
    python manage.py migrate
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations appliquees avec succes" -ForegroundColor Green
    } else {
        throw "Erreur lors de l'application des migrations"
    }

    Write-Host "`n📋 ETAPE 5: Creation du superutilisateur" -ForegroundColor Yellow
    Write-Host "Veuillez entrer les informations pour le superutilisateur:" -ForegroundColor Cyan
    python manage.py createsuperuser

    Write-Host "`n$("=" * 60)" -ForegroundColor Cyan
    Write-Host "🎉 REINITIALISATION TERMINEE AVEC SUCCES!" -ForegroundColor Green
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "✅ Nouvelle base de donnees creee" -ForegroundColor Green
    Write-Host "✅ Tables creees selon la nouvelle structure" -ForegroundColor Green
    Write-Host "✅ Pret a demarrer l'application" -ForegroundColor Green
    Write-Host "`nPour demarrer le serveur:" -ForegroundColor Cyan
    Write-Host "  python manage.py runserver" -ForegroundColor White

} catch {
    Write-Host "`n❌ ERREUR FATALE: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Verifiez que Django est bien installe et configure" -ForegroundColor Yellow
}
