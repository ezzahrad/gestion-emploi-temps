# 🛠️ Guide de Dépannage - AppGET

Ce guide vous aide à résoudre les problèmes les plus courants lors de l'installation, la configuration et l'utilisation d'AppGET.

---

## 📋 **Table des Matières**

1. [Problèmes d'Installation](#-problèmes-dinstallation)
2. [Erreurs de Base de Données](#️-erreurs-de-base-de-données)
3. [Problèmes de Serveur](#-problèmes-de-serveur)
4. [Erreurs API](#-erreurs-api)
5. [Problèmes PDF](#-problèmes-pdf)
6. [Notifications](#-notifications)
7. [Performance](#-performance)
8. [Docker](#-docker)
9. [Frontend](#-frontend)
10. [Logs et Diagnostics](#-logs-et-diagnostics)

---

## 🔧 **Problèmes d'Installation**

### **Erreur : Python non trouvé**
```bash
# Erreur
python: command not found

# Solution
# Sur Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Sur macOS
brew install python3

# Sur Windows
# Téléchargez Python depuis python.org
# Assurez-vous d'ajouter Python au PATH
```

### **Erreur : Node.js non trouvé**
```bash
# Erreur
node: command not found

# Solution
# Sur Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Sur macOS
brew install node

# Sur Windows
# Téléchargez depuis nodejs.org
```

### **Erreur : Dépendances manquantes**
```bash
# Erreur
ERROR: Could not install packages due to an EnvironmentError

# Solution Backend
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade
pip install reportlab Pillow

# Solution Frontend
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### **Erreur : Permissions refusées**
```bash
# Erreur
PermissionError: [Errno 13] Permission denied

# Solution Linux/Mac
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh

# Solution Windows
# Exécuter PowerShell en tant qu'administrateur
```

---

## 🗄️ **Erreurs de Base de Données**

### **Erreur : Connection refusée PostgreSQL**
```bash
# Erreur
psycopg2.OperationalError: could not connect to server

# Diagnostic
sudo systemctl status postgresql
sudo netstat -tlnp | grep 5432

# Solutions
# 1. Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 2. Vérifier la configuration
sudo nano /etc/postgresql/*/main/postgresql.conf
# Décommenter : listen_addresses = '*'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Ajouter : host all all 0.0.0.0/0 md5

# 3. Redémarrer
sudo systemctl restart postgresql
```

### **Erreur : Base de données n'existe pas**
```bash
# Erreur
django.db.utils.OperationalError: database "appget_db" does not exist

# Solution
sudo -u postgres psql
CREATE DATABASE appget_db;
CREATE USER appget_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE appget_db TO appget_user;
\q

# Ensuite
cd backend
python manage.py migrate
```

### **Erreur : Migrations en conflit**
```bash
# Erreur
django.db.migrations.exceptions.InconsistentMigrationHistory

# Solution
cd backend

# Option 1 - Reset migrations (ATTENTION: perte de données)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate

# Option 2 - Fake migrations
python manage.py migrate --fake-initial
python manage.py migrate
```

### **Erreur : Table n'existe pas**
```bash
# Erreur
django.db.utils.ProgrammingError: relation "auth_user" does not exist

# Solution
cd backend
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌐 **Problèmes de Serveur**

### **Erreur : Port déjà utilisé**
```bash
# Erreur
OSError: [Errno 98] Address already in use

# Diagnostic
sudo netstat -tlnp | grep :8000
lsof -ti:8000

# Solution
# Tuer le processus
sudo kill -9 $(lsof -ti:8000)

# Ou utiliser un port différent
python manage.py runserver 0.0.0.0:8001
```

### **Erreur : ALLOWED_HOSTS**
```bash
# Erreur
DisallowedHost at /
Invalid HTTP_HOST header

# Solution
# Dans backend/schedule_management/settings.py
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'votre-domaine.com'
]

# Ou dans .env
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com
```

### **Erreur : CORS (Cross-Origin)**
```bash
# Erreur
Access to XMLHttpRequest has been blocked by CORS policy

# Solution
# Installer django-cors-headers
pip install django-cors-headers

# Dans settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
```

---

## 🔌 **Erreurs API**

### **Erreur : 403 Forbidden**
```bash
# Erreur
HTTP 403 Forbidden

# Diagnostic
# Vérifier l'authentification
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/grades/

# Solutions
# 1. Vérifier le token JWT
python manage.py shell
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='your_username')
refresh = RefreshToken.for_user(user)
print(f"Access: {refresh.access_token}")

# 2. Vérifier les permissions
# Dans votre vue
from rest_framework.permissions import IsAuthenticated
class YourView(APIView):
    permission_classes = [IsAuthenticated]
```

### **Erreur : 500 Internal Server Error**
```bash
# Erreur
HTTP 500 Internal Server Error

# Diagnostic
# Activer le debug temporairement
DEBUG = True

# Vérifier les logs
tail -f logs/django.log

# Ou avec Docker
docker-compose logs -f web
```

### **Erreur : Validation des données**
```bash
# Erreur
{"field": ["This field is required."]}

# Solution Frontend
const validateData = (data) => {
  const errors = {};
  
  if (!data.name) {
    errors.name = "Ce champ est requis";
  }
  
  if (!data.email || !/\S+@\S+\.\S+/.test(data.email)) {
    errors.email = "Email invalide";
  }
  
  return errors;
};
```

---

## 📄 **Problèmes PDF**

### **Erreur : ReportLab manquant**
```bash
# Erreur
ModuleNotFoundError: No module named 'reportlab'

# Solution
pip install reportlab Pillow
```

### **Erreur : Permissions fichier PDF**
```bash
# Erreur
PermissionError: [Errno 13] Permission denied: '/pdf_exports/'

# Solution
mkdir -p pdf_exports pdf_temp
chmod 755 pdf_exports pdf_temp
chown $USER:$USER pdf_exports pdf_temp

# Avec Docker
docker-compose exec web mkdir -p /app/pdf_exports /app/pdf_temp
docker-compose exec web chown -R appget:appget /app/pdf_exports /app/pdf_temp
```

### **Erreur : Timeout génération PDF**
```bash
# Erreur
TimeoutError: PDF generation timeout

# Solution
# Dans settings.py
PDF_EXPORT_SETTINGS = {
    'MAX_FILE_SIZE_MB': 50,
    'TIMEOUT_SECONDS': 300,  # Augmenter le timeout
    'MAX_PAGES': 1000,       # Augmenter si nécessaire
}

# Vérifier Celery
celery -A schedule_management status
```

### **Erreur : Police manquante**
```bash
# Erreur
TTFError: Can't find font file

# Solution
# Sur Ubuntu/Debian
sudo apt install ttf-dejavu-core ttf-dejavu-extra
sudo apt install fonts-liberation

# Dans le générateur PDF
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Utiliser des polices système
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
```

---

## 🔔 **Notifications**

### **Erreur : Celery worker inactif**
```bash
# Erreur
No worker nodes available

# Diagnostic
celery -A schedule_management status
celery -A schedule_management inspect active

# Solution
# Démarrer worker
celery -A schedule_management worker --loglevel=info

# Avec Docker
docker-compose restart celery
docker-compose logs celery
```

### **Erreur : Redis connection**
```bash
# Erreur
redis.exceptions.ConnectionError

# Diagnostic
redis-cli ping

# Solution
# Démarrer Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Avec Docker
docker-compose restart redis
```

### **Erreur : Email non envoyé**
```bash
# Erreur
SMTPAuthenticationError

# Solution
# Vérifier la configuration email dans .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Tester l'envoi
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Message test', 'from@example.com', ['to@example.com'])
```

---

## ⚡ **Performance**

### **Requêtes lentes**
```bash
# Diagnostic
# Activer le debug toolbar
pip install django-debug-toolbar

# Dans settings.py
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]

INTERNAL_IPS = ['127.0.0.1']
```

### **Mémoire insuffisante**
```bash
# Erreur
MemoryError

# Solution
# Optimiser les requêtes
queryset = Grade.objects.select_related('student', 'evaluation').prefetch_related('evaluations')

# Pagination
from django.core.paginator import Paginator
paginator = Paginator(queryset, 25)  # 25 objets par page

# Cache Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### **Frontend lent**
```bash
# Diagnostic
npm run build -- --analyze

# Solutions
# 1. Code splitting
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

# 2. Memoization
const MemoizedComponent = React.memo(ExpensiveComponent);

# 3. Optimiser les images
npm install imagemin imagemin-webpack-plugin
```

---

## 🐳 **Docker**

### **Erreur : Docker daemon non démarré**
```bash
# Erreur
Cannot connect to the Docker daemon

# Solution
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Puis redémarrer la session
```

### **Erreur : Port occupé**
```bash
# Erreur
port is already allocated

# Solution
docker-compose down
docker-compose up -d

# Ou modifier les ports dans docker-compose.yml
ports:
  - "8001:8000"  # Au lieu de 8000:8000
```

### **Erreur : Volume permissions**
```bash
# Erreur
Permission denied in Docker volume

# Solution
# Dans docker-compose.yml
volumes:
  - ./backend:/app:Z  # SELinux compatible

# Ou changer ownership
sudo chown -R 1000:1000 backend/
```

### **Erreur : Build échoue**
```bash
# Erreur
Docker build fails

# Solution
# Nettoyer et rebuilder
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 💻 **Frontend**

### **Erreur : Module non trouvé**
```bash
# Erreur
Module not found: Can't resolve 'component'

# Solution
# Vérifier le chemin d'import
import { Component } from './components/Component';  # Correct
import { Component } from 'components/Component';    # Vérifier alias

# Vérifier la configuration des alias dans vite.config.ts
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
},
```

### **Erreur : TypeScript**
```bash
# Erreur
Property does not exist on type

# Solution
# Vérifier les types
interface Props {
  data: any;  // Éviter 'any', utiliser des types spécifiques
}

# Ou update des types
npm install @types/node @types/react @types/react-dom --save-dev
```

### **Erreur : Build production**
```bash
# Erreur
Build fails in production

# Diagnostic
npm run build
npm run preview

# Solution
# Vérifier les variables d'environnement
VITE_API_BASE_URL=http://your-domain.com

# Optimiser le bundle
npm install --save-dev vite-bundle-analyzer
```

---

## 📊 **Logs et Diagnostics**

### **Activer les logs détaillés**
```python
# Dans settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'grades': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### **Commandes de diagnostic**
```bash
# État des services
systemctl status postgresql redis-server nginx

# Processus AppGET
ps aux | grep python
ps aux | grep node
ps aux | grep celery

# Ports ouverts
sudo netstat -tlnp | grep -E ':(8000|5432|6379|80|443)'

# Espace disque
df -h
du -sh backend/media backend/pdf_exports

# Logs système
journalctl -u your-service -f
tail -f /var/log/nginx/error.log

# Avec Docker
docker-compose ps
docker-compose logs -f
docker stats
```

### **Script de diagnostic automatique**
```bash
#!/bin/bash
# diagnostic.sh

echo "=== AppGET Diagnostic ==="
echo "Date: $(date)"
echo ""

echo "=== Versions ==="
python3 --version
node --version
docker --version
docker-compose --version
echo ""

echo "=== Services ==="
systemctl is-active postgresql || echo "PostgreSQL: STOPPED"
systemctl is-active redis || echo "Redis: STOPPED"
systemctl is-active nginx || echo "Nginx: STOPPED"
echo ""

echo "=== Ports ==="
netstat -tlnp | grep -E ':(8000|5432|6379|80|443)' || echo "Aucun port AppGET détecté"
echo ""

echo "=== Disk Usage ==="
df -h | grep -E '(/$|/var|/opt)'
echo ""

echo "=== Database Connection ==="
python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('Database: OK')
except Exception as e:
    print(f'Database: ERROR - {e}')
"

echo ""
echo "=== Recent Errors ==="
tail -5 django.log 2>/dev/null || echo "Aucun log Django trouvé"
```

---

## 🆘 **Cas d'Urgence**

### **Site complètement inaccessible**
```bash
# 1. Vérifier les services critiques
sudo systemctl status nginx postgresql redis

# 2. Redémarrer les services
sudo systemctl restart nginx
sudo systemctl restart postgresql

# 3. Avec Docker
docker-compose down
docker-compose up -d

# 4. Vérifier les logs
tail -f /var/log/nginx/error.log
docker-compose logs -f web
```

### **Corruption de base de données**
```bash
# 1. Arrêter l'application
sudo systemctl stop your-app-service

# 2. Restaurer depuis la sauvegarde
./scripts/restore.sh BACKUP_ID

# 3. Vérifier l'intégrité
python manage.py check --deploy
python manage.py migrate --check
```

### **Perte de données**
```bash
# 1. Arrêter immédiatement l'application
docker-compose down

# 2. Ne pas redémarrer
# 3. Restaurer depuis la sauvegarde la plus récente
./scripts/restore.sh --list
./scripts/restore.sh LATEST_BACKUP_ID

# 4. Vérifier les données restaurées avant redémarrage
```

---

## 📞 **Obtenir de l'Aide**

### **Avant de demander de l'aide**
1. ✅ Consultez ce guide de dépannage
2. ✅ Vérifiez les logs d'erreur
3. ✅ Reproduisez le problème
4. ✅ Notez votre environnement (OS, versions, etc.)

### **Informations à inclure**
```bash
# Collectez ces informations
echo "OS: $(uname -a)"
echo "Python: $(python3 --version)"
echo "Node: $(node --version)"
echo "Docker: $(docker --version)"
echo "AppGET: $(cat VERSION 2>/dev/null || echo 'Unknown')"

# Logs récents
echo "=== Django Logs ==="
tail -20 django.log

echo "=== Docker Logs ==="
docker-compose logs --tail=20
```

### **Canaux de Support**
- 🐛 **GitHub Issues** : [Créer une issue](../../issues/new)
- 💬 **Discussions** : [GitHub Discussions](../../discussions)
- 📧 **Email** : support@appget.com
- 📚 **Documentation** : [Guide complet](./NOUVELLES_FONCTIONNALITES.md)

---

## ✅ **Prévention**

### **Meilleures Pratiques**
1. **Sauvegardez régulièrement** avec `./scripts/backup.sh`
2. **Testez en développement** avant la production
3. **Surveillez les logs** régulièrement
4. **Mettez à jour** les dépendances de sécurité
5. **Documentez** les configurations personnalisées

### **Monitoring Préventif**
```bash
# Cron jobs recommandés
# Sauvegarde quotidienne à 2h
0 2 * * * /opt/appget/scripts/backup.sh

# Vérification santé chaque heure
0 * * * * /opt/appget/scripts/healthcheck.sh

# Nettoyage hebdomadaire des logs
0 3 * * 0 find /var/log/appget -name "*.log" -mtime +30 -delete
```

---

*Ce guide est maintenu à jour avec les problèmes les plus fréquemment rencontrés. N'hésitez pas à proposer des améliorations !*

<function_calls>
<invoke name="gestion_edt:write_file">
<parameter name="content"># 🛠️ Guide de Dépannage - AppGET

Ce guide vous aide à résoudre les problèmes les plus courants lors de l'installation, la configuration et l'utilisation d'AppGET.

---

## 📋 **Table des Matières**

1. [Problèmes d'Installation](#-problèmes-dinstallation)
2. [Erreurs de Base de Données](#️-erreurs-de-base-de-données)
3. [Problèmes de Serveur](#-problèmes-de-serveur)
4. [Erreurs API](#-erreurs-api)
5. [Problèmes PDF](#-problèmes-pdf)
6. [Notifications](#-notifications)
7. [Performance](#-performance)
8. [Docker](#-docker)
9. [Frontend](#-frontend)
10. [Logs et Diagnostics](#-logs-et-diagnostics)

---

## 🔧 **Problèmes d'Installation**

### **Erreur : Python non trouvé**
```bash
# Erreur
python: command not found

# Solution
# Sur Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Sur macOS
brew install python3

# Sur Windows
# Téléchargez Python depuis python.org
# Assurez-vous d'ajouter Python au PATH
```

### **Erreur : Node.js non trouvé**
```bash
# Erreur
node: command not found

# Solution
# Sur Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Sur macOS
brew install node

# Sur Windows
# Téléchargez depuis nodejs.org
```

### **Erreur : Dépendances manquantes**
```bash
# Erreur
ERROR: Could not install packages due to an EnvironmentError

# Solution Backend
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade
pip install reportlab Pillow

# Solution Frontend
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### **Erreur : Permissions refusées**
```bash
# Erreur
PermissionError: [Errno 13] Permission denied

# Solution Linux/Mac
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh

# Solution Windows
# Exécuter PowerShell en tant qu'administrateur
```

---

## 🗄️ **Erreurs de Base de Données**

### **Erreur : Connection refusée PostgreSQL**
```bash
# Erreur
psycopg2.OperationalError: could not connect to server

# Diagnostic
sudo systemctl status postgresql
sudo netstat -tlnp | grep 5432

# Solutions
# 1. Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 2. Vérifier la configuration
sudo nano /etc/postgresql/*/main/postgresql.conf
# Décommenter : listen_addresses = '*'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Ajouter : host all all 0.0.0.0/0 md5

# 3. Redémarrer
sudo systemctl restart postgresql
```

### **Erreur : Base de données n'existe pas**
```bash
# Erreur
django.db.utils.OperationalError: database "appget_db" does not exist

# Solution
sudo -u postgres psql
CREATE DATABASE appget_db;
CREATE USER appget_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE appget_db TO appget_user;
\q

# Ensuite
cd backend
python manage.py migrate
```

### **Erreur : Migrations en conflit**
```bash
# Erreur
django.db.migrations.exceptions.InconsistentMigrationHistory

# Solution
cd backend

# Option 1 - Reset migrations (ATTENTION: perte de données)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate

# Option 2 - Fake migrations
python manage.py migrate --fake-initial
python manage.py migrate
```

### **Erreur : Table n'existe pas**
```bash
# Erreur
django.db.utils.ProgrammingError: relation "auth_user" does not exist

# Solution
cd backend
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌐 **Problèmes de Serveur**

### **Erreur : Port déjà utilisé**
```bash
# Erreur
OSError: [Errno 98] Address already in use

# Diagnostic
sudo netstat -tlnp | grep :8000
lsof -ti:8000

# Solution
# Tuer le processus
sudo kill -9 $(lsof -ti:8000)

# Ou utiliser un port différent
python manage.py runserver 0.0.0.0:8001
```

### **Erreur : ALLOWED_HOSTS**
```bash
# Erreur
DisallowedHost at /
Invalid HTTP_HOST header

# Solution
# Dans backend/schedule_management/settings.py
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'votre-domaine.com'
]

# Ou dans .env
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com
```

### **Erreur : CORS (Cross-Origin)**
```bash
# Erreur
Access to XMLHttpRequest has been blocked by CORS policy

# Solution
# Installer django-cors-headers
pip install django-cors-headers

# Dans settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
```

---

## 🔌 **Erreurs API**

### **Erreur : 403 Forbidden**
```bash
# Erreur
HTTP 403 Forbidden

# Diagnostic
# Vérifier l'authentification
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/grades/

# Solutions
# 1. Vérifier le token JWT
python manage.py shell
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='your_username')
refresh = RefreshToken.for_user(user)
print(f"Access: {refresh.access_token}")

# 2. Vérifier les permissions
# Dans votre vue
from rest_framework.permissions import IsAuthenticated
class YourView(APIView):
    permission_classes = [IsAuthenticated]
```

### **Erreur : 500 Internal Server Error**
```bash
# Erreur
HTTP 500 Internal Server Error

# Diagnostic
# Activer le debug temporairement
DEBUG = True

# Vérifier les logs
tail -f logs/django.log

# Ou avec Docker
docker-compose logs -f web
```

### **Erreur : Validation des données**
```bash
# Erreur
{"field": ["This field is required."]}

# Solution Frontend
const validateData = (data) => {
  const errors = {};
  
  if (!data.name) {
    errors.name = "Ce champ est requis";
  }
  
  if (!data.email || !/\S+@\S+\.\S+/.test(data.email)) {
    errors.email = "Email invalide";
  }
  
  return errors;
};
```

---

## 📄 **Problèmes PDF**

### **Erreur : ReportLab manquant**
```bash
# Erreur
ModuleNotFoundError: No module named 'reportlab'

# Solution
pip install reportlab Pillow
```

### **Erreur : Permissions fichier PDF**
```bash
# Erreur
PermissionError: [Errno 13] Permission denied: '/pdf_exports/'

# Solution
mkdir -p pdf_exports pdf_temp
chmod 755 pdf_exports pdf_temp
chown $USER:$USER pdf_exports pdf_temp

# Avec Docker
docker-compose exec web mkdir -p /app/pdf_exports /app/pdf_temp
docker-compose exec web chown -R appget:appget /app/pdf_exports /app/pdf_temp
```

### **Erreur : Timeout génération PDF**
```bash
# Erreur
TimeoutError: PDF generation timeout

# Solution
# Dans settings.py
PDF_EXPORT_SETTINGS = {
    'MAX_FILE_SIZE_MB': 50,
    'TIMEOUT_SECONDS': 300,  # Augmenter le timeout
    'MAX_PAGES': 1000,       # Augmenter si nécessaire
}

# Vérifier Celery
celery -A schedule_management status
```

### **Erreur : Police manquante**
```bash
# Erreur
TTFError: Can't find font file

# Solution
# Sur Ubuntu/Debian
sudo apt install ttf-dejavu-core ttf-dejavu-extra
sudo apt install fonts-liberation

# Dans le générateur PDF
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Utiliser des polices système
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
```

---

## 🔔 **Notifications**

### **Erreur : Celery worker inactif**
```bash
# Erreur
No worker nodes available

# Diagnostic
celery -A schedule_management status
celery -A schedule_management inspect active

# Solution
# Démarrer worker
celery -A schedule_management worker --loglevel=info

# Avec Docker
docker-compose restart celery
docker-compose logs celery
```

### **Erreur : Redis connection**
```bash
# Erreur
redis.exceptions.ConnectionError

# Diagnostic
redis-cli ping

# Solution
# Démarrer Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Avec Docker
docker-compose restart redis
```

### **Erreur : Email non envoyé**
```bash
# Erreur
SMTPAuthenticationError

# Solution
# Vérifier la configuration email dans .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Tester l'envoi
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Message test', 'from@example.com', ['to@example.com'])
```

---

## ⚡ **Performance**

### **Requêtes lentes**
```bash
# Diagnostic
# Activer le debug toolbar
pip install django-debug-toolbar

# Dans settings.py
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]

INTERNAL_IPS = ['127.0.0.1']
```

### **Mémoire insuffisante**
```bash
# Erreur
MemoryError

# Solution
# Optimiser les requêtes
queryset = Grade.objects.select_related('student', 'evaluation').prefetch_related('evaluations')

# Pagination
from django.core.paginator import Paginator
paginator = Paginator(queryset, 25)  # 25 objets par page

# Cache Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### **Frontend lent**
```bash
# Diagnostic
npm run build -- --analyze

# Solutions
# 1. Code splitting
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

# 2. Memoization
const MemoizedComponent = React.memo(ExpensiveComponent);

# 3. Optimiser les images
npm install imagemin imagemin-webpack-plugin
```

---

## 🐳 **Docker**

### **Erreur : Docker daemon non démarré**
```bash
# Erreur
Cannot connect to the Docker daemon

# Solution
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Puis redémarrer la session
```

### **Erreur : Port occupé**
```bash
# Erreur
port is already allocated

# Solution
docker-compose down
docker-compose up -d

# Ou modifier les ports dans docker-compose.yml
ports:
  - "8001:8000"  # Au lieu de 8000:8000
```

### **Erreur : Volume permissions**
```bash
# Erreur
Permission denied in Docker volume

# Solution
# Dans docker-compose.yml
volumes:
  - ./backend:/app:Z  # SELinux compatible

# Ou changer ownership
sudo chown -R 1000:1000 backend/
```

### **Erreur : Build échoue**
```bash
# Erreur
Docker build fails

# Solution
# Nettoyer et rebuilder
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 💻 **Frontend**

### **Erreur : Module non trouvé**
```bash
# Erreur
Module not found: Can't resolve 'component'

# Solution
# Vérifier le chemin d'import
import { Component } from './components/Component';  # Correct
import { Component } from 'components/Component';    # Vérifier alias

# Vérifier la configuration des alias dans vite.config.ts
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
},
```

### **Erreur : TypeScript**
```bash
# Erreur
Property does not exist on type

# Solution
# Vérifier les types
interface Props {
  data: any;  // Éviter 'any', utiliser des types spécifiques
}

# Ou update des types
npm install @types/node @types/react @types/react-dom --save-dev
```

### **Erreur : Build production**
```bash
# Erreur
Build fails in production

# Diagnostic
npm run build
npm run preview

# Solution
# Vérifier les variables d'environnement
VITE_API_BASE_URL=http://your-domain.com

# Optimiser le bundle
npm install --save-dev vite-bundle-analyzer
```

---

## 📊 **Logs et Diagnostics**

### **Activer les logs détaillés**
```python
# Dans settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'grades': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### **Commandes de diagnostic**
```bash
# État des services
systemctl status postgresql redis-server nginx

# Processus AppGET
ps aux | grep python
ps aux | grep node
ps aux | grep celery

# Ports ouverts
sudo netstat -tlnp | grep -E ':(8000|5432|6379|80|443)'

# Espace disque
df -h
du -sh backend/media backend/pdf_exports

# Logs système
journalctl -u your-service -f
tail -f /var/log/nginx/error.log

# Avec Docker
docker-compose ps
docker-compose logs -f
docker stats
```

---

## 📞 **Obtenir de l'Aide**

### **Canaux de Support**
- 🐛 **GitHub Issues** : [Créer une issue](../../issues/new)
- 💬 **Discussions** : [GitHub Discussions](../../discussions)
- 📧 **Email** : support@appget.com
- 📚 **Documentation** : [Guide complet](./NOUVELLES_FONCTIONNALITES.md)

---

*Ce guide est maintenu à jour avec les problèmes les plus fréquemment rencontrés. N'hésitez pas à proposer des améliorations !*
