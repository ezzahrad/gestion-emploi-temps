# 🚀 Guide d'Installation AppGET

Ce guide vous accompagne pas à pas dans l'installation complète d'AppGET sur votre système.

## 📋 Prérequis Système

### 🖥️ Configuration Minimale
- **OS** : Windows 10+, Ubuntu 20.04+, macOS 10.15+
- **RAM** : 4 GB minimum (8 GB recommandé)
- **Stockage** : 2 GB d'espace libre
- **Réseau** : Connexion internet pour téléchargement des dépendances

### 📦 Logiciels Requis

#### **Python 3.8+**
```bash
# Vérifier la version Python
python --version  # ou python3 --version

# Installation Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# Installation CentOS/RHEL
sudo yum install python3 python3-pip

# Installation macOS (avec Homebrew)
brew install python@3.11

# Windows : Télécharger depuis https://python.org
```

#### **Node.js 18+**
```bash
# Vérifier la version Node.js
node --version

# Installation Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installation macOS (avec Homebrew)
brew install node@18

# Installation CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Windows : Télécharger depuis https://nodejs.org
```

#### **Base de Données (Optionnel)**
```bash
# PostgreSQL (recommandé pour production)
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows : Télécharger depuis https://www.postgresql.org

# SQLite est inclus avec Python (parfait pour développement)
```

#### **Redis (Optionnel - pour cache avancé)**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows : Utiliser WSL ou Docker
```

## 🎯 Méthodes d'Installation

### 🚀 Méthode 1 : Installation Automatique (Recommandée)

Cette méthode utilise les scripts d'installation automatique fournis.

#### **Étape 1 : Téléchargement**
```bash
# Cloner le projet
git clone https://github.com/votre-repo/appget.git
cd appget

# Ou télécharger et extraire l'archive ZIP
wget https://github.com/votre-repo/appget/archive/main.zip
unzip main.zip && cd appget-main
```

#### **Étape 2 : Lancement Automatique**

**🐧 Linux / 🍎 macOS :**
```bash
# Rendre le script exécutable
chmod +x start_enhanced_appget.sh

# Lancer l'installation et démarrage
./start_enhanced_appget.sh
```

**🪟 Windows :**
```batch
# Double-cliquer ou exécuter en ligne de commande
start_enhanced_appget.bat
```

#### **Ce que fait le script automatique :**
1. ✅ Vérifie les prérequis système
2. ✅ Crée l'environnement virtuel Python
3. ✅ Installe toutes les dépendances backend
4. ✅ Configure la base de données SQLite
5. ✅ Exécute les migrations Django
6. ✅ Installe les dépendances frontend
7. ✅ Compile les assets
8. ✅ Lance les serveurs de développement
9. ✅ Ouvre l'application dans le navigateur

---

### 🛠️ Méthode 2 : Installation Manuelle

Pour plus de contrôle sur le processus d'installation.

#### **Étape 1 : Préparation du Projet**
```bash
# Cloner et naviguer
git clone https://github.com/votre-repo/appget.git
cd appget

# Vérifier la structure
ls -la
# Vous devriez voir : backend/ frontend/ docker/ scripts/ etc.
```

#### **Étape 2 : Configuration Backend Django**

```bash
# Naviguer vers le backend
cd backend

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Vérifier l'activation (vous devriez voir (venv) dans le prompt)
which python  # Doit pointer vers venv/bin/python
```

#### **Étape 3 : Installation des Dépendances Python**
```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances de base
pip install -r requirements.txt

# Installer les dépendances des nouvelles fonctionnalités
pip install reportlab Pillow celery redis

# Vérifier l'installation
pip list | grep -E "(django|reportlab|pillow)"
```

#### **Étape 4 : Configuration de la Base de Données**

**Option A : SQLite (Développement - Recommandée)**
```bash
# SQLite est configuré par défaut
# Rien à faire de spécial !
```

**Option B : PostgreSQL (Production)**
```bash
# 1. Créer la base de données
sudo -u postgres createdb appget_db
sudo -u postgres createuser appget_user

# 2. Configurer les permissions
sudo -u postgres psql
postgres=# ALTER USER appget_user WITH PASSWORD 'votre_mot_de_passe';
postgres=# GRANT ALL PRIVILEGES ON DATABASE appget_db TO appget_user;
postgres=# \q

# 3. Modifier settings.py (ou créer un .env)
cp .env.example .env
# Éditer .env avec vos paramètres PostgreSQL
```

#### **Étape 5 : Migrations et Configuration Django**
```bash
# Exécuter les migrations existantes
python manage.py migrate

# Migrer les nouvelles fonctionnalités
python migrate_enhanced_features.py

# Créer un superutilisateur
python manage.py createsuperuser
# Utiliser : admin / admin123 (ou vos propres identifiants)

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Tester le serveur backend
python manage.py runserver
# Accès : http://127.0.0.1:8000/admin
```

#### **Étape 6 : Configuration Frontend React**
```bash
# Ouvrir un nouveau terminal et naviguer vers frontend
cd ../frontend  # ou cd frontend depuis la racine

# Installer les dépendances Node.js
npm install

# Vérifier l'installation
npm ls react typescript vite

# Configuration optionnelle
cp .env.example .env
# Éditer .env si nécessaire
```

#### **Étape 7 : Compilation et Démarrage Frontend**
```bash
# Développement (avec hot reload)
npm run dev
# Accès : http://localhost:5173

# Ou build pour production
npm run build
npm run preview  # Pour tester le build
```

---

### 🐳 Méthode 3 : Installation Docker

Parfait pour un déploiement rapide et isolation complète.

#### **Étape 1 : Installation Docker**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# macOS : Installer Docker Desktop
# Windows : Installer Docker Desktop

# Vérifier l'installation
docker --version
docker-compose --version
```

#### **Étape 2 : Configuration Docker**
```bash
# Cloner le projet
git clone https://github.com/votre-repo/appget.git
cd appget

# Vérifier les fichiers Docker
ls docker-compose.yml Dockerfile

# Configuration optionnelle
cp .env.example .env
# Éditer .env pour l'environnement Docker
```

#### **Étape 3 : Démarrage avec Docker Compose**
```bash
# Build et démarrage de tous les services
docker-compose up -d --build

# Vérifier les conteneurs
docker-compose ps

# Voir les logs
docker-compose logs -f web

# Accès aux applications
# Frontend : http://localhost:5173
# Backend : http://localhost:8000
```

#### **Étape 4 : Configuration Initiale Docker**
```bash
# Exécuter les migrations dans le conteneur
docker-compose exec web python manage.py migrate

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Migrer les nouvelles fonctionnalités
docker-compose exec web python migrate_enhanced_features.py
```

---

## 🔧 Configuration Post-Installation

### 📧 Configuration Email (Optionnel)
```python
# Dans backend/schedule_management/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'
DEFAULT_FROM_EMAIL = 'AppGET <votre-email@gmail.com>'
```

### 🔐 Configuration Sécurité
```python
# Générer une nouvelle SECRET_KEY pour production
# Dans settings.py ou .env
SECRET_KEY = 'votre-nouvelle-clé-secrète-très-longue-et-complexe'

# Configurer ALLOWED_HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'votre-domaine.com']
```

### 📊 Configuration Redis/Celery (Optionnel)
```python
# Dans settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Démarrer les workers Celery (nouveau terminal)
cd backend
celery -A schedule_management worker --loglevel=info

# Démarrer le scheduler Celery (nouveau terminal)
celery -A schedule_management beat --loglevel=info
```

## ✅ Validation de l'Installation

### 🧪 Tests Automatiques
```bash
# Script de validation complète
python validate_features.py

# Tests backend spécifiques
cd backend
python tests/test_enhanced_features.py

# Tests frontend
cd frontend
npm test

# Test de l'API
curl http://127.0.0.1:8000/api/health/
```

### 🔍 Vérifications Manuelles

#### **Backend Django**
1. ✅ Accéder à http://127.0.0.1:8000/admin
2. ✅ Se connecter avec admin/admin123
3. ✅ Vérifier la présence des nouveaux modules :
   - Grades
   - Absences
   - PDF Export
   - Notifications

#### **Frontend React**
1. ✅ Accéder à http://localhost:5173
2. ✅ Page d'accueil se charge correctement
3. ✅ Navigation fonctionnelle
4. ✅ Pas d'erreurs dans la console navigateur

#### **APIs**
```bash
# Test API status
curl http://127.0.0.1:8000/api/health/

# Test API docs
# Accéder à : http://127.0.0.1:8000/api/docs/
```

### 📋 Checklist Post-Installation

- [ ] **Serveur Backend** fonctionne (port 8000)
- [ ] **Serveur Frontend** fonctionne (port 5173)
- [ ] **Accès Admin** possible avec identifiants
- [ ] **Base de données** migrée correctement
- [ ] **Nouvelles fonctionnalités** visibles dans l'admin
- [ ] **API Documentation** accessible
- [ ] **Tests** passent sans erreur
- [ ] **Logs** sans erreurs critiques

## 🐛 Résolution de Problèmes

### ❌ Problèmes Courants et Solutions

#### **"command not found: python"**
```bash
# Essayer python3
python3 --version

# Créer un alias (Linux/macOS)
echo 'alias python=python3' >> ~/.bashrc
source ~/.bashrc

# Windows : Ajouter Python au PATH
```

#### **"Permission denied"**
```bash
# Linux/macOS : Rendre les scripts exécutables
chmod +x start_enhanced_appget.sh
chmod +x scripts/*.sh

# Vérifier les permissions des dossiers
sudo chown -R $USER:$USER .
```

#### **"Port already in use"**
```bash
# Trouver le processus utilisant le port
# Linux/macOS
lsof -i :8000
lsof -i :5173

# Windows
netstat -ano | findstr :8000

# Tuer le processus
kill -9 <PID>  # Linux/macOS
taskkill /F /PID <PID>  # Windows
```

#### **"Module not found"**
```bash
# Vérifier l'environnement virtuel
which python  # Doit pointer vers venv/

# Réinstaller les dépendances
pip install -r requirements.txt

# Frontend
npm install
```

#### **Erreurs de Migration Django**
```bash
# Reset complet des migrations (ATTENTION : perte de données)
cd backend
rm -rf */migrations/000*.py
python manage.py makemigrations
python manage.py migrate

# Migration des nouvelles fonctionnalités
python migrate_enhanced_features.py
```

#### **Erreurs de Build Frontend**
```bash
cd frontend
# Nettoyer le cache
rm -rf node_modules package-lock.json
npm install

# Problèmes TypeScript
npm run type-check
```

### 🆘 Obtenir de l'Aide

#### **Logs et Débogage**
```bash
# Logs Django détaillés
cd backend
python manage.py runserver --verbosity=2

# Logs frontend détaillés
cd frontend
npm run dev -- --debug

# Docker logs
docker-compose logs -f web
docker-compose logs -f db
```

#### **Support Communautaire**
- **📝 Issues GitHub** : [Créer un ticket](../../issues)
- **💬 Discussions** : [Forum communautaire](../../discussions)
- **📚 Wiki** : [Documentation complète](../../wiki)
- **📧 Email** : support@appget.com

---

## 🎯 Prochaines Étapes

### 🌟 Après l'Installation

1. **📚 Lire la documentation** :
   - [Guide des Fonctionnalités](./NOUVELLES_FONCTIONNALITES.md)
   - [Guide de Déploiement](./DEPLOIEMENT_PRODUCTION.md)

2. **🧪 Explorer les fonctionnalités** :
   - Créer des utilisateurs de test
   - Tester le système de notes
   - Essayer l'export PDF

3. **⚙️ Personnaliser** :
   - Configurer les paramètres institutionnels
   - Adapter les templates
   - Intégrer avec vos systèmes existants

4. **🚀 Déployer en production** :
   - Suivre le guide de déploiement
   - Configurer HTTPS
   - Mettre en place les sauvegardes

### 🎓 Formation

- **Administrateurs** : Configuration et gestion
- **Enseignants** : Utilisation du système de notes
- **Étudiants** : Navigation et fonctionnalités

---

<div align="center">

## 🎉 Félicitations ! AppGET est maintenant installé ! 🚀

**Prêt à transformer votre gestion académique ?**

[🖥️ Accéder à l'App](http://localhost:5173) • [⚙️ Admin Panel](http://127.0.0.1:8000/admin) • [📚 Documentation](../../wiki)

---

**Besoin d'aide ?** [💬 Support](../../issues) • **Problème ?** [🐛 Bug Report](../../issues/new)

*Développé avec ❤️ pour l'éducation moderne*

</div>