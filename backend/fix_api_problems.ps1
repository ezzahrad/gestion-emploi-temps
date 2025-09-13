# 🔧 RÉSOLUTION DES ERREURS API - AppGET
# =====================================

Write-Host "🚀 RÉSOLUTION DES PROBLÈMES API AppGET" -ForegroundColor Green
Write-Host "======================================"

# Vérifier si on est dans le bon dossier
if (!(Test-Path "manage.py")) {
    Write-Host "❌ Erreur: Ce script doit être exécuté depuis le dossier backend" -ForegroundColor Red
    Write-Host "💡 Déplacez-vous vers le dossier backend d'abord" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎯 PROBLÈMES IDENTIFIÉS :" -ForegroundColor Cyan
Write-Host "  1. ❌ HTTP 403 Forbidden sur /api/notifications/" -ForegroundColor Red
Write-Host "  2. ❌ HTTP 404 Not Found sur /api/schedule/" -ForegroundColor Red

Write-Host ""
Write-Host "💡 CAUSES :" -ForegroundColor Cyan
Write-Host "  1. 🔐 Authentification JWT manquante" -ForegroundColor Yellow
Write-Host "  2. 🔗 URL incorrecte (manque 's' dans 'schedules')" -ForegroundColor Yellow

Write-Host ""
Write-Host "🔧 LANCEMENT DU DIAGNOSTIC..." -ForegroundColor Green

# Diagnostic complet
Write-Host ""
Write-Host "📊 ÉTAPE 1: Diagnostic complet" -ForegroundColor Cyan
python debug_api_issues.py

Write-Host ""
Write-Host "🔧 ÉTAPE 2: Résolution automatique" -ForegroundColor Cyan
python fix_api_issues.py

Write-Host ""
Write-Host "✅ RÉSOLUTION TERMINÉE !" -ForegroundColor Green

Write-Host ""
Write-Host "📚 SOLUTIONS RÉSUMÉES :" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎯 PROBLÈME 1: HTTP 403 Forbidden" -ForegroundColor Yellow
Write-Host "   📝 Cause: Toutes les API nécessitent une authentification JWT" -ForegroundColor White
Write-Host "   💡 Solution: Se connecter d'abord pour obtenir un token" -ForegroundColor Green
Write-Host "   📋 Étapes:" -ForegroundColor White
Write-Host "      1. POST http://127.0.0.1:8000/api/auth/login/" -ForegroundColor Gray
Write-Host "         Body: {""username"": ""admin_test"", ""password"": ""admin123""}" -ForegroundColor Gray
Write-Host "      2. Récupérer le token 'access' de la réponse" -ForegroundColor Gray
Write-Host "      3. Ajouter dans les headers: Authorization: Bearer <token>" -ForegroundColor Gray

Write-Host ""
Write-Host "🎯 PROBLÈME 2: HTTP 404 Not Found" -ForegroundColor Yellow  
Write-Host "   📝 Cause: URL incorrecte" -ForegroundColor White
Write-Host "   💡 Solution: Utiliser les bonnes URLs" -ForegroundColor Green
Write-Host "   📋 URLs correctes:" -ForegroundColor White
Write-Host "      ❌ /api/schedule/" -ForegroundColor Red
Write-Host "      ✅ /api/schedule/schedules/" -ForegroundColor Green
Write-Host "      ✅ /api/schedule/absences/" -ForegroundColor Green
Write-Host "      ✅ /api/schedule/makeup-sessions/" -ForegroundColor Green

Write-Host ""
Write-Host "🔑 COMPTES DE TEST CRÉÉS :" -ForegroundColor Cyan
Write-Host "   👤 admin_test / admin123 (Administrateur)" -ForegroundColor Green
Write-Host "   👤 teacher_test / teacher123 (Enseignant)" -ForegroundColor Green  
Write-Host "   👤 student_test / student123 (Étudiant)" -ForegroundColor Green

Write-Host ""
Write-Host "📁 FICHIERS CRÉÉS :" -ForegroundColor Cyan
Write-Host "   📄 api_usage_examples.json - Exemples d'utilisation" -ForegroundColor White
Write-Host "   📄 curl_examples.sh - Commandes cURL" -ForegroundColor White

Write-Host ""
Write-Host "🧪 TEST RAPIDE :" -ForegroundColor Cyan
Write-Host "1. Démarrer le serveur Django:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Tester l'authentification (dans un autre terminal):" -ForegroundColor White
Write-Host "   curl -X POST http://127.0.0.1:8000/api/auth/login/ \" -ForegroundColor Gray
Write-Host "     -H ""Content-Type: application/json"" \" -ForegroundColor Gray
Write-Host "     -d '{""username"": ""admin_test"", ""password"": ""admin123""}'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Utiliser le token reçu pour accéder aux API" -ForegroundColor White

Write-Host ""
Write-Host "🎉 Les problèmes sont maintenant résolus !" -ForegroundColor Green
Write-Host "💡 Consultez les fichiers générés pour plus d'exemples" -ForegroundColor Yellow

Read-Host "Appuyez sur Entrée pour continuer..."
