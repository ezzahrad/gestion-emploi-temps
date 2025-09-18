#!/bin/bash

# 💾 AppGET - Script de Sauvegarde Automatique
# Sauvegarde complète de la base de données, fichiers media et configuration

set -e  # Arrêter le script en cas d'erreur

# Configuration
BACKUP_DIR="/opt/backups/appget"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
LOG_FILE="/var/log/appget_backup.log"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

# Créer le répertoire de sauvegarde
create_backup_directory() {
    log "Création du répertoire de sauvegarde..."
    mkdir -p "$BACKUP_DIR"
    chmod 755 "$BACKUP_DIR"
    log_success "Répertoire de sauvegarde créé: $BACKUP_DIR"
}

# Sauvegarde de la base de données
backup_database() {
    log "Sauvegarde de la base de données..."
    
    # Déterminer le type de base de données
    if command -v docker-compose &> /dev/null && docker-compose ps db &> /dev/null; then
        # Docker Compose
        log "Utilisation de Docker Compose pour la sauvegarde..."
        docker-compose exec -T db pg_dump -U appget_user appget_db > "$BACKUP_DIR/database_$DATE.sql"
    elif [ -n "$DATABASE_URL" ]; then
        # URL de base de données directe
        log "Utilisation de l'URL de base de données..."
        pg_dump "$DATABASE_URL" > "$BACKUP_DIR/database_$DATE.sql"
    else
        # SQLite (développement)
        log "Sauvegarde SQLite..."
        cp backend/db.sqlite3 "$BACKUP_DIR/database_$DATE.sqlite3" 2>/dev/null || log_warning "Fichier SQLite introuvable"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Base de données sauvegardée: database_$DATE.sql"
    else
        log_error "Échec de la sauvegarde de la base de données"
        return 1
    fi
}

# Sauvegarde des fichiers media
backup_media_files() {
    log "Sauvegarde des fichiers media..."
    
    MEDIA_DIRS=("backend/media" "backend/pdf_exports" "backend/static")
    
    for dir in "${MEDIA_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            log "Sauvegarde de $dir..."
            tar -czf "$BACKUP_DIR/$(basename $dir)_$DATE.tar.gz" -C "$(dirname $dir)" "$(basename $dir)"
            if [ $? -eq 0 ]; then
                log_success "$(basename $dir) sauvegardé"
            else
                log_error "Échec sauvegarde de $dir"
            fi
        else
            log_warning "Répertoire $dir introuvable, ignoré"
        fi
    done
}

# Sauvegarde de la configuration
backup_configuration() {
    log "Sauvegarde de la configuration..."
    
    CONFIG_FILES=(".env" "docker-compose.yml" "backend/schedule_management/settings.py")
    CONFIG_BACKUP_DIR="$BACKUP_DIR/config_$DATE"
    mkdir -p "$CONFIG_BACKUP_DIR"
    
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$CONFIG_BACKUP_DIR/"
            log_success "Configuration sauvegardée: $(basename $file)"
        else
            log_warning "Fichier de configuration $file introuvable"
        fi
    done
    
    # Créer une archive de la configuration
    tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$BACKUP_DIR" "config_$DATE"
    rm -rf "$CONFIG_BACKUP_DIR"
    log_success "Configuration archivée: config_$DATE.tar.gz"
}

# Sauvegarde des logs
backup_logs() {
    log "Sauvegarde des logs..."
    
    LOG_DIRS=("logs" "backend/logs" "/var/log/nginx" "/var/log/appget")
    
    for dir in "${LOG_DIRS[@]}"; do
        if [ -d "$dir" ] && [ "$(ls -A $dir 2>/dev/null)" ]; then
            log "Sauvegarde des logs de $dir..."
            tar -czf "$BACKUP_DIR/logs_$(basename $dir)_$DATE.tar.gz" -C "$(dirname $dir)" "$(basename $dir)"
            if [ $? -eq 0 ]; then
                log_success "Logs de $(basename $dir) sauvegardés"
            else
                log_warning "Échec sauvegarde logs de $dir"
            fi
        fi
    done
}

# Vérification de l'intégrité des sauvegardes
verify_backups() {
    log "Vérification de l'intégrité des sauvegardes..."
    
    # Vérifier les fichiers créés
    BACKUP_FILES=(
        "database_$DATE.sql"
        "media_$DATE.tar.gz"
        "pdf_exports_$DATE.tar.gz"
        "config_$DATE.tar.gz"
    )
    
    for file in "${BACKUP_FILES[@]}"; do
        if [ -f "$BACKUP_DIR/$file" ]; then
            SIZE=$(stat -f%z "$BACKUP_DIR/$file" 2>/dev/null || stat -c%s "$BACKUP_DIR/$file" 2>/dev/null)
            if [ "$SIZE" -gt 0 ]; then
                log_success "Fichier $file vérifié (${SIZE} bytes)"
            else
                log_error "Fichier $file vide"
            fi
        else
            log_warning "Fichier $file introuvable"
        fi
    done
}

# Nettoyage des anciennes sauvegardes
cleanup_old_backups() {
    log "Nettoyage des anciennes sauvegardes (> $RETENTION_DAYS jours)..."
    
    if [ -d "$BACKUP_DIR" ]; then
        DELETED=$(find "$BACKUP_DIR" -name "*.sql" -o -name "*.tar.gz" -o -name "*.sqlite3" | \
                 xargs ls -t | tail -n +$((RETENTION_DAYS * 4)) | wc -l)
        
        find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete
        find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
        find "$BACKUP_DIR" -name "*.sqlite3" -mtime +$RETENTION_DAYS -delete
        
        if [ "$DELETED" -gt 0 ]; then
            log_success "$DELETED anciennes sauvegardes supprimées"
        else
            log "Aucune ancienne sauvegarde à supprimer"
        fi
    fi
}

# Envoi de notification (optionnel)
send_notification() {
    local status=$1
    local message=$2
    
    # Notification par email (si configurée)
    if [ -n "$BACKUP_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "AppGET Backup - $status" "$BACKUP_EMAIL"
        log "Notification email envoyée à $BACKUP_EMAIL"
    fi
    
    # Webhook Discord/Slack (si configuré)
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-Type: application/json' \
             -d "{\"text\": \"AppGET Backup - $status: $message\"}" \
             "$WEBHOOK_URL" &>/dev/null
        log "Notification webhook envoyée"
    fi
}

# Génération du rapport de sauvegarde
generate_backup_report() {
    log "Génération du rapport de sauvegarde..."
    
    REPORT_FILE="$BACKUP_DIR/backup_report_$DATE.json"
    
    cat > "$REPORT_FILE" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "backup_id": "$DATE",
    "status": "completed",
    "files": [
$(find "$BACKUP_DIR" -name "*$DATE*" -type f | sed 's/.*/"&",/' | sed '$ s/,$//')
    ],
    "total_size": "$(du -sh "$BACKUP_DIR" | cut -f1)",
    "retention_policy": "${RETENTION_DAYS} days",
    "next_backup": "$(date -d '+1 day' -Iseconds)"
}
EOF
    
    log_success "Rapport de sauvegarde généré: $REPORT_FILE"
}

# Fonction principale
main() {
    log "🚀 DÉBUT DE LA SAUVEGARDE APPGET"
    log "=================================="
    
    # Vérifier les prérequis
    if [ "$EUID" -eq 0 ]; then
        log_warning "Exécution en tant que root détectée"
    fi
    
    # Étapes de sauvegarde
    STEPS=(
        "create_backup_directory"
        "backup_database"
        "backup_media_files"
        "backup_configuration"
        "backup_logs"
        "verify_backups"
        "cleanup_old_backups"
        "generate_backup_report"
    )
    
    FAILED_STEPS=0
    
    for step in "${STEPS[@]}"; do
        if $step; then
            log_success "Étape $step terminée"
        else
            log_error "Échec de l'étape $step"
            ((FAILED_STEPS++))
        fi
    done
    
    # Résumé final
    log "=================================="
    if [ $FAILED_STEPS -eq 0 ]; then
        log_success "🎉 SAUVEGARDE TERMINÉE AVEC SUCCÈS"
        send_notification "SUCCESS" "Sauvegarde AppGET terminée avec succès ($DATE)"
    else
        log_error "⚠️ SAUVEGARDE TERMINÉE AVEC $FAILED_STEPS ERREUR(S)"
        send_notification "WARNING" "Sauvegarde AppGET terminée avec $FAILED_STEPS erreur(s) ($DATE)"
    fi
    
    log "Répertoire de sauvegarde: $BACKUP_DIR"
    log "Taille totale: $(du -sh "$BACKUP_DIR" | cut -f1)"
    log "Prochaine sauvegarde recommandée: $(date -d '+1 day' '+%Y-%m-%d')"
    
    return $FAILED_STEPS
}

# Configuration depuis variables d'environnement
BACKUP_DIR="${APPGET_BACKUP_DIR:-$BACKUP_DIR}"
RETENTION_DAYS="${APPGET_BACKUP_RETENTION:-$RETENTION_DAYS}"
BACKUP_EMAIL="${APPGET_BACKUP_EMAIL:-}"
WEBHOOK_URL="${APPGET_BACKUP_WEBHOOK:-}"

# Exécution du script
main "$@"
exit $?
