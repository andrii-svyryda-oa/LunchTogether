#!/bin/bash
set -e

BACKUP_DIR="/var/backups/lunchtogether"
DB_NAME="lunchtogether"
DB_USER="lunchtogether"
DB_PASSWORD="DB_PASSWORD_PLACEHOLDER"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lunchtogether_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
echo "Creating database backup..."
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# Set permissions
chmod 600 $BACKUP_FILE

# Delete old backups
find $BACKUP_DIR -name "lunchtogether_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup created: $BACKUP_FILE"
