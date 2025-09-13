#!/bin/bash

echo "🔧 Test rapide d'AppGET Frontend"
echo "================================"
echo

# Vérifications préliminaires
echo "📋 Vérifications..."

# Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js non installé"
    exit 1
else
    echo "✅ Node.js $(node --version)"
fi

# NPM
if ! command -v npm &> /dev/null; then
    echo "❌ NPM non installé"
    exit 1
else
    echo "✅ NPM $(npm --version)"
fi

# Dossier frontend
if [ ! -f "package.json" ]; then
    echo "❌ Pas dans le dossier frontend"
    exit 1
else
    echo "✅ Dossier frontend trouvé"
fi

echo
echo "🚀 Démarrage du test..."

# Démarrage rapide
echo "Starting Vite dev server..."
timeout 10s npm run dev || true

echo
echo "✅ Test terminé !"
echo "🌐 Ouvrez http://localhost:5173 dans votre navigateur"