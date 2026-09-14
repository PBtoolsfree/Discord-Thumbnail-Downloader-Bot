#!/bin/bash
set -e

echo "========================================"
echo "PB Thumbnail Bot - Installer"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found! Please install Docker and Docker Compose first."
    exit 1
fi

# Create data directories
mkdir -p data tmp
chmod 777 data tmp

# Generate .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    
    # Generate random setup password
    RANDOM_PASS=$(openssl rand -hex 8)
    sed -i "s/change_this_default_password/$RANDOM_PASS/" .env
    # Ensure permissions for Docker non-root user
    chmod 666 .env
    chmod -R 777 data tmp 2>/dev/null || true
    echo "Generated Setup Password: $RANDOM_PASS"
    echo "Keep this safe! You'll need it to log into the web setup."
else
    echo ".env already exists. Skipping creation."
fi

# Build and start
echo "Building and starting Docker containers..."
docker compose up -d --build

SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")

echo "========================================"
echo "Installation Complete!"
echo ""
echo "Setup Dashboard:"
echo "http://$SERVER_IP:8080"
echo "Username: admin"
echo "(Check above for your generated password if this is a fresh install)"
echo ""
echo "Commands:"
echo "Logs: docker compose logs -f"
echo "Stop: docker compose down"
echo "========================================"
