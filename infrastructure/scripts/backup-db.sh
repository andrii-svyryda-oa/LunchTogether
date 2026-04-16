#!/bin/bash
set -e

BACKUP_DIR="/var/backups/lunchtogether"
DB_NAME="lunchtogether"
DB_USER="lunchtogether"
SECRETS_FILE="/etc/lunchtogether/backup.env"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lunchtogether_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

if [ ! -r "$SECRETS_FILE" ]; then
    echo "Error: cannot read $SECRETS_FILE (must be created by setup.sh with the DB password)." >&2
    exit 1
fi

# shellcheck disable=SC1090
source "$SECRETS_FILE"

if [ -z "${PGPASSWORD:-}" ]; then
    echo "Error: PGPASSWORD not set in $SECRETS_FILE" >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "Creating database backup..."
pg_dump -U "$DB_USER" -h localhost "$DB_NAME" | gzip > "$BACKUP_FILE"

chmod 600 "$BACKUP_FILE"

find "$BACKUP_DIR" -name "lunchtogether_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup created: $BACKUP_FILE"
