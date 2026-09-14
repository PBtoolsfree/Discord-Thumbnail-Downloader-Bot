#!/bin/bash
set -e

echo "Updating PB Thumbnail Bot..."

# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build

echo "Update complete! Containers are restarting."
docker compose logs --tail=10
