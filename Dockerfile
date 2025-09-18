# Dockerfile pour AppGET avec nouvelles fonctionnalités
FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=schedule_management.settings
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    gettext \
    postgresql-client \
    libpq-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash appget

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY backend/requirements.txt /app/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer les nouvelles dépendances pour les fonctionnalités avancées
RUN pip install --no-cache-dir \
    reportlab==4.0.7 \
    Pillow>=9.0.0 \
    celery>=5.3.0 \
    redis>=4.5.0 \
    django-cors-headers>=4.3.0

# Copier le code de l'application
COPY backend/ /app/

# Créer les répertoires nécessaires
RUN mkdir -p /app/media /app/static /app/pdf_exports /app/pdf_temp

# Ajuster les permissions
RUN chown -R appget:appget /app

# Changer vers l'utilisateur non-root
USER appget

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || true

# Exposer le port
EXPOSE 8000

# Script de démarrage
COPY docker/entrypoint.sh /app/entrypoint.sh
USER root
RUN chmod +x /app/entrypoint.sh
USER appget

# Commande par défaut
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
