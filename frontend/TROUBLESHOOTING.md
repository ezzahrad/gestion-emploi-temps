# 🔧 Guide de Dépannage - Frontend AppGET

## ❌ Problème Résolu : "Dynamic require not supported"

### 🎯 Cause du Problème
L'erreur venait de l'utilisation de `require()` dans les fichiers de configuration Vite/Tailwind, qui n'est pas compatible avec les modules ES6.

### ✅ Corrections Appliquées

#### 1. **vite.config.ts**
- ❌ Supprimé les `require()` dans la configuration PostCSS
- ✅ Configuration PostCSS déplacée vers `postcss.config.js`
- ✅ Proxy API Django configuré correctement

#### 2. **tailwind.config.js**
- ❌ Supprimé `require('@tailwindcss/forms')` etc.
- ✅ Utilisé `import` avec syntaxe ES6
- ✅ Plugins Tailwind importés correctement

#### 3. **postcss.config.js**
- ✅ Configuration simplifiée avec `export default`
- ✅ Plugins de base Tailwind + Autoprefixer

## 🚀 Test de la Correction

### Option 1 - Script Automatique
```cmd
cd frontend
fix_and_start.bat
```

### Option 2 - Manuel
```bash
cd frontend

# Nettoyage
rm -rf node_modules package-lock.json .vite

# Réinstallation
npm install

# Test de TypeScript
npm run type-check

# Démarrage
npm run dev
```

## 🔍 Vérifications Supplémentaires

### ✅ Node.js Version
```bash
node --version  # Doit être >= 18.0.0
npm --version   # Doit être >= 9.0.0
```

### ✅ Dépendances Critiques
```json
{
  "vite": "^5.0.0",
  "tailwindcss": "^3.3.5",
  "@vitejs/plugin-react": "^4.1.1"
}
```

### ✅ Variables d'Environnement
Créer le fichier `.env` si absent :
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_URL=http://localhost:5173
```

## 🆘 Si le Problème Persiste

### Erreur "Cannot resolve module"
```bash
# Réinstaller avec force
npm ci --force
```

### Erreur TypeScript
```bash
# Vérifier tsconfig.json
npm run type-check
```

### Erreur de port
```bash
# Changer le port dans vite.config.ts
server: { port: 3001 }
```

### Cache Vite corrompu
```bash
rm -rf .vite
rm -rf dist
npm run dev
```

## 📋 Checklist de Dépannage

- [ ] Node.js >= 18.0.0 installé
- [ ] Dossier `node_modules` supprimé et réinstallé
- [ ] Fichier `.env` présent avec bonnes URLs
- [ ] Backend Django démarré sur port 8000
- [ ] Aucun autre processus sur port 5173
- [ ] Configuration `vite.config.ts` sans `require()`
- [ ] Configuration `tailwind.config.js` avec `import`
- [ ] TypeScript sans erreurs (`npm run type-check`)

## 🎉 Confirmation du Succès

Quand tout fonctionne, vous devriez voir :
```bash
  VITE v5.0.0  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

## 📞 Support

Si le problème persiste après ces étapes :

1. **Copier l'erreur complète** dans le terminal
2. **Vérifier les logs** du navigateur (F12 → Console)
3. **Tester la connexion backend** : http://127.0.0.1:8000/api/
4. **Utiliser la page de test** : http://localhost:5173/connection-test

---

**✅ Configuration corrigée pour un fonctionnement optimal !**