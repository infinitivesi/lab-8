#!/usr/bin/env bash
# Backup SQLite DB from docker volume to host backups/ directory with timestamp
set -euo pipefail

BACKUP_DIR="$(pwd)/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
CONTAINER_NAME="laba-5-backup-temp"
VOLUME_NAME="laba-5_db_data"

# Use a temporary container to copy from volume to host
docker run --rm -v ${VOLUME_NAME}:/data -v ${BACKUP_DIR}:/backup alpine sh -c "cp /data/db.sqlite /backup/db-${TIMESTAMP}.sqlite && chmod 600 /backup/db-${TIMESTAMP}.sqlite"

echo "Backup saved to ${BACKUP_DIR}/db-${TIMESTAMP}.sqlite"
