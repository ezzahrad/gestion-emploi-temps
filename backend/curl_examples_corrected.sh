#!/bin/bash
# 🔧 EXEMPLES CURL CORRIGÉS - API AppGET
# =====================================

echo "🔑 1. AUTHENTIFICATION"
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_test", "password": "admin123"}'

echo ""
echo "📋 2. NOTIFICATIONS (avec token)"
curl -X GET http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Bearer <VOTRE_TOKEN_JWT>"

echo ""
echo "📅 3. EMPLOIS DU TEMPS"
curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ \
  -H "Authorization: Bearer <VOTRE_TOKEN_JWT>"

echo ""
echo "🏛️ 4. DÉPARTEMENTS"
curl -X GET http://127.0.0.1:8000/api/core/departments/ \
  -H "Authorization: Bearer <VOTRE_TOKEN_JWT>"

echo ""
echo "📚 5. PROGRAMMES"
curl -X GET http://127.0.0.1:8000/api/core/programs/ \
  -H "Authorization: Bearer <VOTRE_TOKEN_JWT>"

echo ""
echo "👨‍🏫 6. ENSEIGNANTS"
curl -X GET http://127.0.0.1:8000/api/core/teachers/ \
  -H "Authorization: Bearer <VOTRE_TOKEN_JWT>"

echo ""
echo "🏢 7. SALLES"
curl -X GET http://127.0.0.1:8000/api/core/rooms/ \
  -H "Authorization: Bearer <VOTRE_TOKEN_JWT>"

echo ""
echo "⚡ 8. STATUS (sans token)"
curl -X GET http://127.0.0.1:8000/status/

echo ""
echo "✅ Tests terminés !"
