#!/bin/bash
set -e

echo "Backing up PB Thumbnail Bot data..."
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup .env safely
cp .env $BACKUP_DIR/
# Backup DB
cp -r data/ $BACKUP_DIR/

echo "Backup created at $BACKUP_DIR"
