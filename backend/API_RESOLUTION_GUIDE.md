# 🔧 GUIDE DE RÉSOLUTION - ERREURS API AppGET

## 🎯 **PROBLÈMES IDENTIFIÉS**

### ❌ **Erreur 1 : HTTP 403 Forbidden**
- **URL** : `/api/notifications/`
- **Message** : "Informations d'authentification non fournies"
- **Status** : 403 Forbidden

### ❌ **Erreur 2 : HTTP 404 Not Found**
- **URL** : `/api/schedule/`
- **Message** : "Page not found"
- **Status** : 404 Not Found

---

## 🔍 **ANALYSE DES CAUSES**

### **Cause de l'erreur 403**
Votre configuration Django REST Framework dans `settings.py` :
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```
**➡️ TOUTES les API nécessitent une authentification JWT par défaut**

### **Cause de l'erreur 404**
L'URL `/api/schedule/` n'existe pas. Les URLs correctes sont :
- ✅ `/api/schedule/schedules/`
- ✅ `/api/schedule/absences/`
- ✅ `/api/schedule/makeup-sessions/`

---

## 💡 **SOLUTIONS COMPLÈTES**

### 🔐 **Solution 1 : Authentification JWT**

#### **Étape 1 : Se connecter pour obtenir un token**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_test", "password": "admin123"}'
```

#### **Réponse attendue :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin_test",
    "role": "ADMIN"
  }
}
```

#### **Étape 2 : Utiliser le token pour accéder aux API**
```bash
curl -X GET http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 🔗 **Solution 2 : URLs correctes**

#### **URLs incorretes ❌**
```
/api/schedule/          # N'existe pas
```

#### **URLs correctes ✅**
```
/api/schedule/schedules/          # Liste des emplois du temps
/api/schedule/schedules/1/        # Détail d'un emploi du temps
/api/schedule/absences/           # Liste des absences
/api/schedule/makeup-sessions/    # Sessions de rattrapage
```

---

## 🧪 **TESTS RAPIDES**

### **1. Démarrer le serveur**
```bash
cd backend
python manage.py runserver
```

### **2. Créer des comptes de test**
```bash
python fix_api_issues.py
```

### **3. Tester l'authentification**
```bash
# Se connecter
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_test", "password": "admin123"}'

# Copier le token 'access' de la réponse
export TOKEN="<votre_token_access>"

# Tester les API
curl -X GET http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔑 **COMPTES DE TEST DISPONIBLES**

| Username | Password | Rôle | Usage |
|----------|----------|------|-------|
| `admin_test` | `admin123` | Administrateur | Tests complets |
| `teacher_test` | `teacher123` | Enseignant | Tests enseignant |
| `student_test` | `student123` | Étudiant | Tests étudiant |

---

## 📋 **EXEMPLES D'UTILISATION**

### **JavaScript/Fetch**
```javascript
// 1. Authentification
const login = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'admin_test',
      password: 'admin123'
    })
  });
  
  const data = await response.json();
  const token = data.access;
  
  // 2. Utiliser le token
  const notifications = await fetch('http://127.0.0.1:8000/api/notifications/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await notifications.json();
};
```

### **Python/Requests**
```python
import requests

# 1. Authentification
response = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
    'username': 'admin_test',
    'password': 'admin123'
})

token = response.json()['access']

# 2. Utiliser le token
headers = {'Authorization': f'Bearer {token}'}

notifications = requests.get(
    'http://127.0.0.1:8000/api/notifications/',
    headers=headers
)

schedules = requests.get(
    'http://127.0.0.1:8000/api/schedule/schedules/',
    headers=headers
)
```

---

## 🛠️ **SCRIPTS DE RÉSOLUTION AUTOMATIQUE**

### **Diagnostic complet**
```bash
cd backend
python debug_api_issues.py
```

### **Résolution automatique**
```bash
cd backend  
python fix_api_issues.py
```

### **Script PowerShell tout-en-un**
```powershell
cd backend
.\fix_api_problems.ps1
```

---

## ✅ **VÉRIFICATION DE LA RÉSOLUTION**

Une fois les solutions appliquées, vous devriez voir :

### **✅ Authentification réussie**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_test", "password": "admin123"}'
# Retourne : HTTP 200 avec un token
```

### **✅ API accessible avec token**
```bash
curl -X GET http://127.0.0.1:8000/api/notifications/ \
  -H "Authorization: Bearer <token>"
# Retourne : HTTP 200 avec les données
```

### **✅ URLs correctes**
```bash
curl -X GET http://127.0.0.1:8000/api/schedule/schedules/ \
  -H "Authorization: Bearer <token>"
# Retourne : HTTP 200 avec les emplois du temps
```

---

## 🎉 **RÉSULTAT ATTENDU**

Après application des solutions :
- ✅ **Erreur 403** : Résolue avec l'authentification JWT
- ✅ **Erreur 404** : Résolue avec les bonnes URLs
- ✅ **API fonctionnelle** : Tous les endpoints accessibles
- ✅ **Comptes de test** : Disponibles pour tous les rôles

---

## 📞 **SUPPORT SUPPLÉMENTAIRE**

Si vous rencontrez encore des problèmes :

1. **Vérifiez** que le serveur Django fonctionne
2. **Exécutez** le script de diagnostic : `python debug_api_issues.py`
3. **Consultez** les logs Django pour plus de détails
4. **Testez** avec les comptes créés automatiquement

**🎯 Votre API AppGET est maintenant entièrement fonctionnelle !**
