@echo off
echo 🚀 TEST MANUEL SIMPLE - API AppGET
echo ================================

echo.
echo 🔑 1. Test d'authentification...
echo Connexion avec admin_test / admin123

curl -X POST http://127.0.0.1:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"admin_test\", \"password\": \"admin123\"}"

echo.
echo.
echo 💡 ÉTAPES SUIVANTES :
echo 1. Copiez le token 'access' de la réponse ci-dessus
echo 2. Remplacez YOUR_TOKEN dans les commandes suivantes
echo 3. Testez les endpoints :

echo.
echo 📋 Test notifications :
echo curl -X GET http://127.0.0.1:8000/api/notifications/ -H "Authorization: Bearer YOUR_TOKEN"

echo.
echo 📅 Test emplois du temps :
echo curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ -H "Authorization: Bearer YOUR_TOKEN"

echo.
echo 🏛️ Test départements :
echo curl -X GET http://127.0.0.1:8000/api/core/departments/ -H "Authorization: Bearer YOUR_TOKEN"

pause
