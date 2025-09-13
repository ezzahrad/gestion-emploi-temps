# fix_vscode_typescript_errors.ps1 - Corriger les erreurs TypeScript dans VS Code

Write-Host "🧹 Nettoyage cache TypeScript et VS Code..." -ForegroundColor Yellow

# Aller dans le dossier frontend
Set-Location "C:\Users\HP\Downloads\appGET\frontend"

# Nettoyer le cache npm
Write-Host "📦 Nettoyage cache npm..." -ForegroundColor Cyan
npm cache clean --force

# Nettoyer node_modules et réinstaller (optionnel)
$reinstall = Read-Host "Voulez-vous réinstaller node_modules? (y/N)"
if ($reinstall -eq "y" -or $reinstall -eq "Y") {
    Write-Host "🗑️  Suppression node_modules..." -ForegroundColor Red
    Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "package-lock.json" -Force -ErrorAction SilentlyContinue
    
    Write-Host "📥 Réinstallation dépendances..." -ForegroundColor Green
    npm install
}

# Nettoyer les fichiers de cache TypeScript
Write-Host "🧹 Nettoyage cache TypeScript..." -ForegroundColor Cyan
Remove-Item -Path "tsconfig.tsbuildinfo" -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".tscache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n✅ Nettoyage terminé!" -ForegroundColor Green

Write-Host "`n🔧 Instructions pour VS Code:" -ForegroundColor Yellow
Write-Host "1. Fermer VS Code complètement (Alt+F4)"
Write-Host "2. Rouvrir VS Code"  
Write-Host "3. Ouvrir la palette de commandes (Ctrl+Shift+P)"
Write-Host "4. Taper: 'TypeScript: Restart TS Server'"
Write-Host "5. Appuyer sur Entrée"

Write-Host "`n🚀 Redémarrer le serveur de développement:" -ForegroundColor Green
Write-Host "npm run dev"

$restart = Read-Host "`nVoulez-vous redémarrer le serveur maintenant? (y/N)"
if ($restart -eq "y" -or $restart -eq "Y") {
    Write-Host "🚀 Démarrage du serveur..." -ForegroundColor Green
    npm run dev
}
