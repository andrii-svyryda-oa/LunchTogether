#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore-db.sh <backup_file>"
    echo "Available backups:"
    ls -lh /var/backups/lunchtogether/
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="lunchtogether"
DB_USER="lunchtogether"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will restore the database from backup and overwrite current data!"
read -p "Are you sure? (yes/no): " -r
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Restore cancelled."
    exit 1
fi

# Stop backend service
echo "Stopping backend service..."
sudo systemctl stop lunchtogether-backend

# Restore database
echo "Restoring database..."
gunzip -c $BACKUP_FILE | sudo -u postgres psql -U $DB_USER $DB_NAME

# Start backend service
echo "Starting backend service..."
sudo systemctl start lunchtogether-backend

echo "Database restored successfully!"
