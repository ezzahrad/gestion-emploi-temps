#!/bin/bash

# 🔄 AppGET - Script de Restauration
# Restaure une sauvegarde complète d'AppGET

set -e

# Configuration
BACKUP_DIR="/opt/backups/appget"
LOG_FILE="/var/log/appget_restore.log"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Afficher l'aide
show_help() {
    echo "🔄 AppGET - Script de Restauration"
    echo ""
    echo "Usage: $0 [OPTIONS] BACKUP_ID"
    echo ""
    echo "Options:"
    echo "  -l, --list              Lister les sauvegardes disponibles"
    echo "  -d, --database-only     Restaurer seulement la base de données"
    echo "  -m, --media-only        Restaurer seulement les fichiers media"
    echo "  -c, --config-only       Restaurer seulement la configuration"
    echo "  -f, --force            Forcer la restauration sans confirmation"
    echo "  -h, --help             Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 --list"
    echo "  $0 20250115_143022"
    echo "  $0 --database-only 20250115_143022"
    echo "  $0 --force 20250115_143022"
}

# Lister les sauvegardes disponibles
list_backups() {
    log "📋 Sauvegardes disponibles dans $BACKUP_DIR:"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Répertoire de sauvegarde introuvable: $BACKUP_DIR"
        return 1
    fi
    
    # Trouver toutes les sauvegardes
    BACKUPS=$(find "$BACKUP_DIR" -name "database_*.sql" -o -name "database_*.sqlite3" | \
              sed 's/.*database_\([0-9_]*\)\..*/\1/' | sort -r)
    
    if [ -z "$BACKUPS" ]; then
        log_warning "Aucune sauvegarde trouvée"
        return 1
    fi
    
    echo "| ID Sauvegarde    | Date             | Taille DB | Fichiers Media |"
    echo "|------------------|------------------|-----------|----------------|"
    
    for backup_id in $BACKUPS; do
        # Convertir l'ID en date lisible
        DATE_PART=$(echo "$backup_id" | cut -d_ -f1)
        TIME_PART=$(echo "$backup_id" | cut -d_ -f2)
        READABLE_DATE="${DATE_PART:0:4}-${DATE_PART:4:2}-${DATE_PART:6:2} ${TIME_PART:0:2}:${TIME_PART:2:2}:${TIME_PART:4:2}"
        
        # Taille de la base de données
        DB_FILE=$(find "$BACKUP_DIR" -name "database_${backup_id}.*" | head -1)
        if [ -f "$DB_FILE" ]; then
            DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
        else
            DB_SIZE="N/A"
        fi
        
        # Fichiers media
        MEDIA_FILE="$BACKUP_DIR/media_${backup_id}.tar.gz"
        if [ -f "$MEDIA_FILE" ]; then
            MEDIA_STATUS="✅"
        else
            MEDIA_STATUS="❌"
        fi
        
        printf "| %-16s | %-16s | %-9s | %-14s |\n" "$backup_id" "$READABLE_DATE" "$DB_SIZE" "$MEDIA_STATUS"
    done
    
    echo ""
    log "Pour restaurer une sauvegarde, utilisez: $0 <BACKUP_ID>"
}

# Vérifier qu'une sauvegarde existe
verify_backup_exists() {
    local backup_id=$1
    
    log "Vérification de l'existence de la sauvegarde $backup_id..."
    
    # Chercher le fichier de base de données
    DB_FILE=$(find "$BACKUP_DIR" -name "database_${backup_id}.*" | head -1)
    if [ ! -f "$DB_FILE" ]; then
        log_error "Fichier de base de données introuvable pour la sauvegarde $backup_id"
        return 1
    fi
    
    log_success "Sauvegarde $backup_id trouvée: $DB_FILE"
    return 0
}

# Arrêter les services
stop_services() {
    log "Arrêt des services AppGET..."
    
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        log "Arrêt des conteneurs Docker..."
        docker-compose down
        log_success "Conteneurs Docker arrêtés"
    elif systemctl is-active --quiet appget; then
        log "Arrêt du service systemd..."
        sudo systemctl stop appget
        log_success "Service AppGET arrêté"
    else
        log_warning "Aucun service actif détecté"
    fi
}

# Démarrer les services
start_services() {
    log "Démarrage des services AppGET..."
    
    if [ -f "docker-compose.yml" ]; then
        log "Démarrage des conteneurs Docker..."
        docker-compose up -d
        log_success "Conteneurs Docker démarrés"
        
        # Attendre que les services soient prêts
        log "Attente de la disponibilité des services..."
        sleep 30
        
        # Vérifier que l'API répond
        for i in {1..30}; do
            if curl -f http://localhost:8000/admin/ &>/dev/null; then
                log_success "API disponible"
                break
            fi
            sleep 2
        done
    elif systemctl list-unit-files appget.service &>/dev/null; then
        log "Démarrage du service systemd..."
        sudo systemctl start appget
        log_success "Service AppGET démarré"
    fi
}

# Restaurer la base de données
restore_database() {
    local backup_id=$1
    
    log "Restauration de la base de données..."
    
    # Trouver le fichier de sauvegarde
    DB_FILE=$(find "$BACKUP_DIR" -name "database_${backup_id}.*" | head -1)
    
    if [[ "$DB_FILE" == *.sql ]]; then
        # PostgreSQL
        log "Restauration PostgreSQL depuis $DB_FILE..."
        
        if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
            # Docker
            log "Restauration via Docker Compose..."
            
            # Recréer la base de données
            docker-compose exec db psql -U appget_user -c "DROP DATABASE IF EXISTS appget_db;"
            docker-compose exec db psql -U appget_user -c "CREATE DATABASE appget_db;"
            
            # Restaurer les données
            cat "$DB_FILE" | docker-compose exec -T db psql -U appget_user -d appget_db
        else
            # Installation directe
            log "Restauration PostgreSQL directe..."
            psql "$DATABASE_URL" < "$DB_FILE"
        fi
        
    elif [[ "$DB_FILE" == *.sqlite3 ]]; then
        # SQLite
        log "Restauration SQLite depuis $DB_FILE..."
        cp "$DB_FILE" "backend/db.sqlite3"
    else
        log_error "Format de base de données non reconnu: $DB_FILE"
        return 1
    fi
    
    log_success "Base de données restaurée"
}

# Restaurer les fichiers media
restore_media() {
    local backup_id=$1
    
    log "Restauration des fichiers media..."
    
    MEDIA_DIRS=("media" "pdf_exports" "static")
    
    for dir in "${MEDIA_DIRS[@]}"; do
        MEDIA_FILE="$BACKUP_DIR/${dir}_${backup_id}.tar.gz"
        
        if [ -f "$MEDIA_FILE" ]; then
            log "Restauration de $dir depuis $MEDIA_FILE..."
            
            # Sauvegarder l'ancien répertoire
            if [ -d "backend/$dir" ]; then
                mv "backend/$dir" "backend/${dir}.backup.$(date +%s)"
            fi
            
            # Extraire la sauvegarde
            tar -xzf "$MEDIA_FILE" -C backend/
            
            log_success "Répertoire $dir restauré"
        else
            log_warning "Fichier media $MEDIA_FILE introuvable"
        fi
    done
}

# Restaurer la configuration
restore_configuration() {
    local backup_id=$1
    
    log "Restauration de la configuration..."
    
    CONFIG_FILE="$BACKUP_DIR/config_${backup_id}.tar.gz"
    
    if [ -f "$CONFIG_FILE" ]; then
        log "Restauration de la configuration depuis $CONFIG_FILE..."
        
        # Créer un répertoire temporaire
        TEMP_DIR=$(mktemp -d)
        tar -xzf "$CONFIG_FILE" -C "$TEMP_DIR"
        
        # Restaurer les fichiers de configuration
        CONFIG_FILES=(".env" "docker-compose.yml")
        
        for file in "${CONFIG_FILES[@]}"; do
            if [ -f "$TEMP_DIR/config_${backup_id}/$file" ]; then
                # Sauvegarder l'ancien fichier
                if [ -f "$file" ]; then
                    mv "$file" "${file}.backup.$(date +%s)"
                fi
                
                # Copier le nouveau fichier
                cp "$TEMP_DIR/config_${backup_id}/$file" "$file"
                log_success "Configuration $file restaurée"
            fi
        done
        
        # Nettoyer le répertoire temporaire
        rm -rf "$TEMP_DIR"
    else
        log_warning "Fichier de configuration $CONFIG_FILE introuvable"
    fi
}

# Exécuter les migrations post-restauration
run_post_restore_migrations() {
    log "Exécution des migrations post-restauration..."
    
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        # Docker
        docker-compose exec web python manage.py migrate
        docker-compose exec web python manage.py collectstatic --noinput
    else
        # Installation directe
        cd backend
        python manage.py migrate
        python manage.py collectstatic --noinput
        cd ..
    fi
    
    log_success "Migrations terminées"
}

# Vérifier l'intégrité après restauration
verify_restore() {
    log "Vérification de l'intégrité de la restauration..."
    
    # Vérifier que l'API répond
    for i in {1..30}; do
        if curl -f http://localhost:8000/admin/ &>/dev/null; then
            log_success "API accessible"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "API inaccessible après restauration"
            return 1
        fi
        sleep 2
    done
    
    # Vérifier la base de données
    if command -v docker-compose &> /dev/null; then
        USER_COUNT=$(docker-compose exec -T db psql -U appget_user -d appget_db -c "SELECT COUNT(*) FROM auth_user;" | grep -E "^\s*[0-9]+\s*$" | tr -d ' ')
        if [ "$USER_COUNT" -gt 0 ]; then
            log_success "Base de données accessible ($USER_COUNT utilisateurs)"
        else
            log_error "Problème avec la base de données"
            return 1
        fi
    fi
    
    log_success "Restauration vérifiée avec succès"
}

# Fonction principale de restauration
restore_backup() {
    local backup_id=$1
    local database_only=$2
    local media_only=$3
    local config_only=$4
    local force=$5
    
    log "🔄 DÉBUT DE LA RESTAURATION APPGET"
    log "====================================="
    log "Sauvegarde à restaurer: $backup_id"
    
    # Vérifier que la sauvegarde existe
    if ! verify_backup_exists "$backup_id"; then
        return 1
    fi
    
    # Demander confirmation sauf si --force
    if [ "$force" != "true" ]; then
        echo ""
        log_warning "⚠️ ATTENTION: Cette opération va remplacer les données actuelles"
        read -p "Êtes-vous sûr de vouloir continuer ? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Restauration annulée par l'utilisateur"
            return 0
        fi
    fi
    
    # Arrêter les services
    stop_services
    
    # Étapes de restauration selon les options
    if [ "$config_only" = "true" ]; then
        restore_configuration "$backup_id"
    elif [ "$media_only" = "true" ]; then
        restore_media "$backup_id"
    elif [ "$database_only" = "true" ]; then
        restore_database "$backup_id"
        run_post_restore_migrations
    else
        # Restauration complète
        restore_database "$backup_id"
        restore_media "$backup_id"
        restore_configuration "$backup_id"
        run_post_restore_migrations
    fi
    
    # Redémarrer les services
    start_services
    
    # Vérifier la restauration
    if verify_restore; then
        log_success "🎉 RESTAURATION TERMINÉE AVEC SUCCÈS"
        log "AppGET a été restauré à partir de la sauvegarde $backup_id"
    else
        log_error "⚠️ PROBLÈMES DÉTECTÉS APRÈS RESTAURATION"
        log "Vérifiez les logs et l'état de l'application"
        return 1
    fi
}

# Analyser les arguments de ligne de commande
BACKUP_ID=""
LIST_BACKUPS=false
DATABASE_ONLY=false
MEDIA_ONLY=false
CONFIG_ONLY=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--list)
            LIST_BACKUPS=true
            shift
            ;;
        -d|--database-only)
            DATABASE_ONLY=true
            shift
            ;;
        -m|--media-only)
            MEDIA_ONLY=true
            shift
            ;;
        -c|--config-only)
            CONFIG_ONLY=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [ -z "$BACKUP_ID" ]; then
                BACKUP_ID="$1"
            else
                log_error "Argument inattendu: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Exécution principale
if [ "$LIST_BACKUPS" = true ]; then
    list_backups
elif [ -n "$BACKUP_ID" ]; then
    restore_backup "$BACKUP_ID" "$DATABASE_ONLY" "$MEDIA_ONLY" "$CONFIG_ONLY" "$FORCE"
else
    log_error "ID de sauvegarde requis"
    show_help
    exit 1
fi
