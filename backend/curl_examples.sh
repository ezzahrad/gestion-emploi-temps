# 🔧 GUIDE CURL - API AppGET
# ===========================

# 1. 🔑 Authentification
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_test", "password": "admin123"}'

# 2. 📋 Notifications (avec token)
curl -X GET http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Bearer <votre_token>"

# 3. 📅 Emplois du temps
curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ \
  -H "Authorization: Bearer <votre_token>"

# 4. 📚 Absences
curl -X GET http://127.0.0.1:8000/api/schedule/absences/ \
  -H "Authorization: Bearer <votre_token>"

# 5. 🏛️ Core API
curl -X GET http://127.0.0.1:8000/api/core/ \
  -H "Authorization: Bearer <votre_token>"

# 6. ⚡ Status
curl -X GET http://127.0.0.1:8000/status/

# 💡 NOTES :
# - Remplacez <votre_token> par votre token réel
# - Les tokens expirent après 7 jours
# - Utilisez le refresh token pour renouveler
