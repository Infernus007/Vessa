#!/bin/bash
#
# VESSA Automated Backup Script
# 
# This script creates backups of the database and application files.
# It should be run via cron for automated backups.
#
# Crontab example (daily at 2 AM):
# 0 2 * * * /opt/vessa/firewall-app/scripts/backup.sh >> /var/log/vessa-backup.log 2>&1
#

set -e  # Exit on error

# Configuration
BACKUP_DIR="/opt/vessa/backups"
APP_DIR="/opt/vessa/firewall-app"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7  # Keep backups for 7 days

# Database credentials (loaded from .env)
if [ -f "$APP_DIR/.env" ]; then
    export $(grep -v '^#' "$APP_DIR/.env" | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "Starting backup process..."

# 1. Database Backup
log "Backing up database..."

DB_BACKUP_FILE="$BACKUP_DIR/vessa_db_$DATE.sql"

if mysqldump \
    --user="$DB_USER" \
    --password="$DB_PASSWORD" \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --single-transaction \
    --routines \
    --triggers \
    "$DB_NAME" > "$DB_BACKUP_FILE"; then
    
    log "Database backup created: $DB_BACKUP_FILE"
    
    # Compress the backup
    gzip "$DB_BACKUP_FILE"
    log "Database backup compressed: $DB_BACKUP_FILE.gz"
    
    # Calculate size
    SIZE=$(du -h "$DB_BACKUP_FILE.gz" | cut -f1)
    log "Backup size: $SIZE"
else
    error "Database backup failed!"
    exit 1
fi

# 2. Application Files Backup (optional)
log "Backing up application files..."

APP_BACKUP_FILE="$BACKUP_DIR/vessa_app_$DATE.tar.gz"

if tar -czf "$APP_BACKUP_FILE" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='node_modules' \
    -C "$(dirname "$APP_DIR")" \
    "$(basename "$APP_DIR")"; then
    
    log "Application files backed up: $APP_BACKUP_FILE"
    
    SIZE=$(du -h "$APP_BACKUP_FILE" | cut -f1)
    log "App backup size: $SIZE"
else
    warning "Application files backup failed (non-critical)"
fi

# 3. Configuration Backup
log "Backing up configuration..."

CONFIG_BACKUP_FILE="$BACKUP_DIR/vessa_config_$DATE.tar.gz"

tar -czf "$CONFIG_BACKUP_FILE" \
    "$APP_DIR/.env" \
    "$APP_DIR/gunicorn.conf.py" \
    /etc/nginx/sites-available/vessa \
    /etc/systemd/system/vessa.service \
    2>/dev/null || warning "Some config files not found (expected on fresh install)"

if [ -f "$CONFIG_BACKUP_FILE" ]; then
    log "Configuration backed up: $CONFIG_BACKUP_FILE"
fi

# 4. Cleanup old backups
log "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."

DELETED_COUNT=0

# Remove database backups older than retention period
find "$BACKUP_DIR" -name "vessa_db_*.sql.gz" -type f -mtime +$RETENTION_DAYS -print -delete | while read file; do
    ((DELETED_COUNT++))
done

# Remove app backups older than retention period
find "$BACKUP_DIR" -name "vessa_app_*.tar.gz" -type f -mtime +$RETENTION_DAYS -print -delete

# Remove config backups older than retention period
find "$BACKUP_DIR" -name "vessa_config_*.tar.gz" -type f -mtime +$RETENTION_DAYS -print -delete

log "Cleanup complete. Removed $DELETED_COUNT old backup(s)"

# 5. Verify latest backup
log "Verifying latest database backup..."

if gzip -t "$DB_BACKUP_FILE.gz"; then
    log "Database backup integrity verified ✓"
else
    error "Database backup verification failed!"
    exit 1
fi

# 6. List current backups
log "Current backups:"
ls -lh "$BACKUP_DIR" | grep "^-" | awk '{print $9 " (" $5 ")"}'

TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Total backup directory size: $TOTAL_SIZE"

# 7. Optional: Upload to S3/Cloud Storage
# Uncomment and configure if using cloud backups
#
# if command -v aws &> /dev/null; then
#     log "Uploading to S3..."
#     aws s3 cp "$DB_BACKUP_FILE.gz" s3://your-bucket/vessa-backups/
#     log "S3 upload complete"
# fi

# 8. Optional: Send notification
# Uncomment to send email notification
#
# HOSTNAME=$(hostname)
# echo "VESSA backup completed successfully on $HOSTNAME at $(date)" | \
#     mail -s "VESSA Backup Success" admin@yourdomain.com

log "Backup process completed successfully!"

exit 0

