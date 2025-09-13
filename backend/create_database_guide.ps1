# create_database_guide.ps1 - Guide interactif pour créer la base de données exemplaire

Write-Host "🎓 CRÉATION BASE DE DONNÉES EXEMPLAIRE - APPGET" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Vérifier qu'on est dans le bon dossier
$currentPath = Get-Location
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erreur: Vous devez être dans le dossier backend!" -ForegroundColor Red
    Write-Host "📁 Exécutez: cd C:\Users\HP\Downloads\appGET\backend" -ForegroundColor Yellow
    exit 1
}

Write-Host "📂 Dossier backend détecté ✅" -ForegroundColor Green

# Étape 1: Vérifier les modèles
Write-Host "`n🔍 ÉTAPE 1: Vérification des modèles Django" -ForegroundColor Cyan
Write-Host "----------------------------------------------------" -ForegroundColor Cyan

try {
    python check_models_ready.py
    $modelsOk = $LASTEXITCODE -eq 0
} catch {
    Write-Host "❌ Erreur lors de la vérification des modèles" -ForegroundColor Red
    $modelsOk = $false
}

if (-not $modelsOk) {
    Write-Host "`n🔧 Tentative d'application des migrations..." -ForegroundColor Yellow
    python manage.py migrate
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Échec des migrations. Veuillez corriger manuellement." -ForegroundColor Red
        exit 1
    }
}

# Étape 2: Choix du type de base de données
Write-Host "`n📋 ÉTAPE 2: Choix du type de base de données" -ForegroundColor Cyan
Write-Host "----------------------------------------------------" -ForegroundColor Cyan
Write-Host "1️⃣  Test rapide    - 8 utilisateurs pour tests d'authentification" -ForegroundColor White
Write-Host "2️⃣  Base complète  - Base de données réaliste avec centaines d'utilisateurs" -ForegroundColor White
Write-Host "3️⃣  Annuler" -ForegroundColor White

do {
    $choice = Read-Host "`nVotre choix (1/2/3)"
    
    switch ($choice) {
        "1" {
            Write-Host "`n⚡ CRÉATION RAPIDE D'UTILISATEURS DE TEST" -ForegroundColor Yellow
            Write-Host "===========================================" -ForegroundColor Yellow
            
            Write-Host "📋 Ce qui sera créé:" -ForegroundColor White
            Write-Host "   👑 2 Administrateurs" -ForegroundColor White
            Write-Host "   🏛️  1 Chef de département" -ForegroundColor White  
            Write-Host "   👨‍🏫 2 Enseignants" -ForegroundColor White
            Write-Host "   👨‍🎓 3 Étudiants" -ForegroundColor White
            
            $confirm = Read-Host "`nConfirmer la création? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-Host "`n🚀 Création en cours..." -ForegroundColor Green
                python create_quick_test_users.py
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "`n✅ UTILISATEURS DE TEST CRÉÉS AVEC SUCCÈS!" -ForegroundColor Green
                    Write-Host "`n📝 Comptes principaux créés:" -ForegroundColor Cyan
                    Write-Host "   👑 Admin: admin@university.ma / admin123" -ForegroundColor White
                    Write-Host "   👨‍🏫 Prof: prof.alami@university.ma / prof123" -ForegroundColor White
                    Write-Host "   👨‍🎓 Étudiant: ahmed.berrada@etu.university.ma / etudiant123" -ForegroundColor White
                    Write-Host "`n📁 Détails complets dans: comptes_test_rapide.txt" -ForegroundColor Yellow
                } else {
                    Write-Host "❌ Erreur lors de la création" -ForegroundColor Red
                }
            }
            break
        }
        
        "2" {
            Write-Host "`n🏛️  CRÉATION BASE DE DONNÉES COMPLÈTE" -ForegroundColor Yellow
            Write-Host "=======================================" -ForegroundColor Yellow
            
            Write-Host "📋 Ce qui sera créé:" -ForegroundColor White
            Write-Host "   🏛️  5 Départements universitaires" -ForegroundColor White
            Write-Host "   📚 20+ Programmes d'études" -ForegroundColor White
            Write-Host "   🏢 100+ Salles" -ForegroundColor White
            Write-Host "   📖 50+ Matières" -ForegroundColor White
            Write-Host "   👥 300-500 Utilisateurs" -ForegroundColor White
            Write-Host "   📅 Emplois du temps d'exemple" -ForegroundColor White
            
            Write-Host "`n⚠️  ATTENTION: Cette opération peut prendre 2-5 minutes" -ForegroundColor Yellow
            
            $confirm = Read-Host "`nConfirmer la création? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-Host "`n🚀 Création en cours (patientez...)..." -ForegroundColor Green
                python create_sample_database.py
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "`n🎉 BASE DE DONNÉES COMPLÈTE CRÉÉE AVEC SUCCÈS!" -ForegroundColor Green
                    Write-Host "`n📝 Mots de passe standards:" -ForegroundColor Cyan
                    Write-Host "   👑 Administrateurs: admin2024" -ForegroundColor White
                    Write-Host "   🏛️  Chefs département: chef2024" -ForegroundColor White
                    Write-Host "   👨‍🏫 Enseignants: prof2024" -ForegroundColor White
                    Write-Host "   👨‍🎓 Étudiants: etudiant2024" -ForegroundColor White
                    Write-Host "`n📁 Liste complète dans: comptes_utilisateurs.txt" -ForegroundColor Yellow
                } else {
                    Write-Host "❌ Erreur lors de la création" -ForegroundColor Red
                }
            }
            break
        }
        
        "3" {
            Write-Host "🚪 Annulation..." -ForegroundColor Yellow
            exit 0
        }
        
        default {
            Write-Host "❌ Choix invalide. Utilisez 1, 2 ou 3." -ForegroundColor Red
        }
    }
} while ($choice -notin @("1", "2", "3"))

# Étape 3: Instructions pour tester
Write-Host "`n🚀 ÉTAPE 3: Tester l'application" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan

Write-Host "1️⃣  Démarrer les serveurs:" -ForegroundColor White
Write-Host "   cd .." -ForegroundColor Gray
Write-Host "   .\start_servers.ps1" -ForegroundColor Gray

Write-Host "`n2️⃣  Ou démarrer manuellement:" -ForegroundColor White
Write-Host "   Backend:  python manage.py runserver" -ForegroundColor Gray
Write-Host "   Frontend: cd ..\frontend && npm run dev" -ForegroundColor Gray

Write-Host "`n3️⃣  Tester la connexion:" -ForegroundColor White
Write-Host "   🌐 Application: http://localhost:3000/login" -ForegroundColor Gray
Write-Host "   🛠️  Django Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Gray

$startServers = Read-Host "`nVoulez-vous démarrer les serveurs maintenant? (y/N)"
if ($startServers -eq "y" -or $startServers -eq "Y") {
    Write-Host "`n🚀 Démarrage des serveurs..." -ForegroundColor Green
    Set-Location ".."
    .\start_servers.ps1
}

Write-Host "`n🎉 Configuration terminée! Bonne exploration d'AppGET!" -ForegroundColor Green