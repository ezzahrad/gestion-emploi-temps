# 🚀 Guide de Déploiement AppGET - Production

## 📋 **Vue d'ensemble**

Ce guide vous accompagne pour déployer AppGET avec toutes ses nouvelles fonctionnalités en production.

---

## 🎯 **Prérequis**

### **Infrastructure**
- **Serveur Linux** (Ubuntu 20.04+ recommandé)
- **RAM** : 4GB minimum, 8GB recommandé
- **Stockage** : 50GB minimum (pour les PDF et médias)
- **CPU** : 2 cores minimum

### **Logiciels**
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** pour le déploiement
- **Certbot** (optionnel, pour HTTPS)

---

## 🛠️ **Installation Rapide**

### **1. Cloner le Projet**
```bash
git clone <your-repo-url> appget
cd appget
```

### **2. Configuration Environnement**
```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer les variables
nano .env
```

### **3. Variables d'Environnement (.env)**
```bash
# Base de données
DATABASE_URL=postgresql://appget_user:STRONG_PASSWORD@db:5432/appget_db
POSTGRES_DB=appget_db
POSTGRES_USER=appget_user
POSTGRES_PASSWORD=STRONG_PASSWORD

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Django
DEBUG=0
SECRET_KEY=your-very-long-secret-key-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (pour notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Sécurité
SECURE_BROWSER_XSS_FILTER=1
SECURE_CONTENT_TYPE_NOSNIFF=1
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=1
SECURE_HSTS_PRELOAD=1

# PDF Export
PDF_MAX_FILE_SIZE_MB=50
PDF_RETENTION_DAYS=7
```

### **4. Déploiement avec Docker**
```bash
# Construction et démarrage
docker-compose up -d --build

# Vérifier les logs
docker-compose logs -f web

# Créer un superutilisateur (si nécessaire)
docker-compose exec web python manage.py createsuperuser
```

---

## 🔧 **Configuration Avancée**

### **1. HTTPS avec Let's Encrypt**
```bash
# Installer Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renouvellement automatique
sudo crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

### **2. Configuration Nginx Production**
```nginx
# /etc/nginx/sites-available/appget
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Sécurité SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/appget/static/;
        expires 1y;
    }

    location /media/ {
        alias /var/appget/media/;
        expires 1y;
    }
}

# Redirection HTTP vers HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### **3. Sauvegarde Automatique**
```bash
#!/bin/bash
# /opt/appget/backup.sh

BACKUP_DIR="/opt/backups/appget"
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde base de données
docker-compose exec -T db pg_dump -U appget_user appget_db > $BACKUP_DIR/db_$DATE.sql

# Sauvegarde fichiers media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /var/appget media/

# Sauvegarde fichiers PDF
tar -czf $BACKUP_DIR/pdf_$DATE.tar.gz -C /var/appget pdf_exports/

# Nettoyage (garder 30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Sauvegarde terminée : $DATE"
```

```bash
# Rendre exécutable et programmer
chmod +x /opt/appget/backup.sh

# Crontab pour sauvegarde quotidienne à 2h
sudo crontab -e
# Ajouter : 0 2 * * * /opt/appget/backup.sh
```

---

## 📊 **Monitoring et Logs**

### **1. Monitoring Docker**
```bash
# Surveiller les conteneurs
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Utilisation des ressources
docker stats

# Logs spécifiques
docker-compose logs web
docker-compose logs celery
docker-compose logs db
```

### **2. Monitoring Application**
```bash
# Endpoint de santé
curl http://localhost:8000/health/

# Statut des tâches Celery
docker-compose exec web python manage.py shell
>>> from celery import current_app
>>> i = current_app.control.inspect()
>>> i.active()
>>> i.scheduled()
```

### **3. Logs Centralisés**
```yaml
# docker-compose.override.yml pour logs
version: '3.8'
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  celery:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🔒 **Sécurité Production**

### **1. Firewall**
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000  # Bloquer l'accès direct à Django
```

### **2. Fail2ban**
```bash
# Installer Fail2ban
sudo apt install fail2ban

# Configuration pour Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6
```

### **3. Mise à jour Sécurité**
```bash
#!/bin/bash
# /opt/appget/security-update.sh

# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Mise à jour images Docker
docker-compose pull

# Redémarrage avec nouvelles images
docker-compose up -d

# Nettoyage
docker system prune -f

echo "Mise à jour sécurité terminée"
```

---

## 📈 **Performance et Optimisation**

### **1. Configuration PostgreSQL**
```sql
-- Optimisations pour production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

SELECT pg_reload_conf();
```

### **2. Configuration Redis**
```bash
# redis.conf optimisations
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### **3. Scaling Horizontal**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  web:
    deploy:
      replicas: 3
  
  celery:
    deploy:
      replicas: 2
```

```bash
# Démarrage avec scaling
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

---

## 🚨 **Dépannage**

### **Problèmes Courants**

#### **1. Erreur de Migration**
```bash
# Réinitialiser les migrations
docker-compose exec web python manage.py migrate --fake-initial
docker-compose exec web python manage.py migrate
```

#### **2. Erreur PDF Export**
```bash
# Vérifier les permissions
docker-compose exec web ls -la pdf_exports/
docker-compose exec web mkdir -p pdf_exports pdf_temp
docker-compose exec web chown -R appget:appget pdf_exports pdf_temp
```

#### **3. Celery Worker Inactif**
```bash
# Redémarrer Celery
docker-compose restart celery celery-beat

# Vérifier les tâches
docker-compose exec web python manage.py shell
>>> from celery import current_app
>>> current_app.control.purge()
```

#### **4. Base de Données Lente**
```bash
# Analyser les requêtes lentes
docker-compose exec db psql -U appget_user -d appget_db -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

### **Logs de Debug**
```bash
# Activer le debug temporairement
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> settings.DEBUG = True

# Logs détaillés
docker-compose logs --tail=100 web
docker-compose logs --tail=100 celery
```

---

## 📞 **Maintenance**

### **1. Tâches Quotidiennes**
```bash
#!/bin/bash
# Tâches de maintenance quotidiennes

# Nettoyage des fichiers PDF expirés
docker-compose exec web python manage.py cleanup_expired_pdfs

# Nettoyage des notifications anciennes
docker-compose exec web python manage.py cleanup_old_notifications

# Optimisation base de données
docker-compose exec db psql -U appget_user -d appget_db -c "VACUUM ANALYZE;"
```

### **2. Tâches Hebdomadaires**
```bash
#!/bin/bash
# Tâches de maintenance hebdomadaires

# Sauvegarde complète
/opt/appget/backup.sh

# Mise à jour sécurité
/opt/appget/security-update.sh

# Rapport d'utilisation
docker-compose exec web python manage.py generate_usage_report
```

### **3. Surveillance Automatique**
```bash
#!/bin/bash
# /opt/appget/healthcheck.sh

# Vérifier les services
if ! curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "ALERTE: AppGET ne répond pas"
    docker-compose restart web
fi

# Vérifier l'espace disque
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "ALERTE: Espace disque faible: ${DISK_USAGE}%"
fi

# Vérifier la mémoire
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "ALERTE: Mémoire faible: ${MEM_USAGE}%"
fi
```

---

## 🎯 **Checklist Déploiement**

### **Avant le Déploiement**
- [ ] Variables d'environnement configurées
- [ ] Certificats SSL obtenus
- [ ] Domaine configuré
- [ ] Sauvegardes testées
- [ ] Monitoring configuré

### **Après le Déploiement**
- [ ] Tests de fonctionnalité
- [ ] Performance vérifiée
- [ ] Sécurité testée
- [ ] Sauvegardes fonctionnelles
- [ ] Documentation à jour

### **Tests Post-Déploiement**
```bash
# Script de test complet
#!/bin/bash

echo "🧪 Tests post-déploiement AppGET"

# Test API
curl -f http://localhost:8000/api/health/ || echo "❌ API indisponible"

# Test authentification
curl -f http://localhost:8000/admin/ || echo "❌ Admin indisponible"

# Test PDF export
curl -f -X POST http://localhost:8000/api/pdf-export/export/create/ || echo "⚠️ PDF export à vérifier"

# Test base de données
docker-compose exec db pg_isready -U appget_user -d appget_db || echo "❌ DB indisponible"

# Test Redis
docker-compose exec redis redis-cli ping || echo "❌ Redis indisponible"

echo "✅ Tests terminés"
```

---

## 📚 **Ressources Supplémentaires**

- **Documentation Django** : https://docs.djangoproject.com/
- **Docker Best Practices** : https://docs.docker.com/develop/best-practices/
- **PostgreSQL Tuning** : https://pgtune.leopard.in.ua/
- **Nginx Configuration** : https://nginx.org/en/docs/

---

## 🆘 **Support**

En cas de problème :
1. Consulter les logs : `docker-compose logs`
2. Vérifier les issues GitHub
3. Contacter l'équipe de développement
4. Documentation complète : `./NOUVELLES_FONCTIONNALITES.md`

**Votre AppGET est maintenant prêt pour la production ! 🚀**
