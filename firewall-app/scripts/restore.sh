#!/bin/bash
#
# VESSA Database Restore Script
#
# This script restores the database from a backup file.
#
# Usage: ./restore.sh <backup_file>
# Example: ./restore.sh /opt/vessa/backups/vessa_db_20251027_020000.sql.gz
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if backup file is provided
if [ -z "$1" ]; then
    error "No backup file specified"
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /opt/vessa/backups/vessa_db_20251027_020000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load database credentials
APP_DIR="/opt/vessa/firewall-app"
if [ -f "$APP_DIR/.env" ]; then
    export $(grep -v '^#' "$APP_DIR/.env" | xargs)
else
    error ".env file not found in $APP_DIR"
    exit 1
fi

log "VESSA Database Restore"
log "======================"
log ""
log "Backup file: $BACKUP_FILE"
log "Database: $DB_NAME"
log "Host: $DB_HOST"
log ""

# Confirm restoration
warning "This will OVERWRITE the current database!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled"
    exit 0
fi

# Stop application
log "Stopping application..."
if systemctl is-active --quiet vessa; then
    sudo systemctl stop vessa
    log "Application stopped"
else
    warning "Application is not running"
fi

# Create a backup of current database before restoring
log "Creating safety backup of current database..."
SAFETY_BACKUP="/tmp/vessa_safety_backup_$(date +%Y%m%d_%H%M%S).sql"
mysqldump \
    --user="$DB_USER" \
    --password="$DB_PASSWORD" \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    "$DB_NAME" > "$SAFETY_BACKUP"

gzip "$SAFETY_BACKUP"
log "Safety backup created: $SAFETY_BACKUP.gz"

# Decompress backup if it's gzipped
TEMP_SQL="/tmp/vessa_restore_temp.sql"

if [[ "$BACKUP_FILE" == *.gz ]]; then
    log "Decompressing backup..."
    gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"
else
    cp "$BACKUP_FILE" "$TEMP_SQL"
fi

# Restore database
log "Restoring database..."

if mysql \
    --user="$DB_USER" \
    --password="$DB_PASSWORD" \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    "$DB_NAME" < "$TEMP_SQL"; then
    
    log "Database restored successfully ✓"
    
    # Clean up temp file
    rm -f "$TEMP_SQL"
    
    # Start application
    log "Starting application..."
    sudo systemctl start vessa
    
    # Wait for application to start
    sleep 5
    
    # Check if application is running
    if systemctl is-active --quiet vessa; then
        log "Application started successfully ✓"
    else
        error "Application failed to start!"
        log "Restoring from safety backup..."
        
        gunzip -c "$SAFETY_BACKUP.gz" | mysql \
            --user="$DB_USER" \
            --password="$DB_PASSWORD" \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            "$DB_NAME"
        
        sudo systemctl start vessa
        error "Restore failed. Original database has been restored."
        exit 1
    fi
    
    # Test health endpoint
    log "Testing application health..."
    sleep 2
    
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        log "Health check passed ✓"
    else
        warning "Health check failed (application may still be starting)"
    fi
    
    log ""
    log "Restore completed successfully!"
    log "Safety backup is available at: $SAFETY_BACKUP.gz"
    log "You can delete it once you've verified everything is working."
    
else
    error "Database restore failed!"
    
    # Clean up
    rm -f "$TEMP_SQL"
    
    # Restore from safety backup
    log "Restoring from safety backup..."
    gunzip -c "$SAFETY_BACKUP.gz" | mysql \
        --user="$DB_USER" \
        --password="$DB_PASSWORD" \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        "$DB_NAME"
    
    sudo systemctl start vessa
    
    error "Restore failed. Original database has been restored."
    exit 1
fi

exit 0


