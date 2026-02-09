#!/bin/bash
set -e

APP_DIR="/var/www/lunchtogether"
APP_USER="lunchtogether"

echo "Deploying LunchTogether..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo"
    exit 1
fi

# Navigate to app directory
cd $APP_DIR

# Pull latest code (will be done by GitHub Actions, but keeping for manual deploys)
if [ -d ".git" ]; then
    echo "1. Pulling latest code..."
    sudo -u $APP_USER git pull
fi

# Deploy Backend
echo "2. Deploying backend..."
cd $APP_DIR/backend

# Install dependencies
echo "   - Installing dependencies..."
sudo -u $APP_USER /home/$APP_USER/.cargo/bin/uv sync

# Run migrations
echo "   - Running database migrations..."
sudo -u $APP_USER /home/$APP_USER/.cargo/bin/uv run alembic upgrade head

# Restart backend service
echo "   - Restarting backend service..."
systemctl restart lunchtogether-backend

# Check backend status
sleep 2
if systemctl is-active --quiet lunchtogether-backend; then
    echo "   Backend is running"
else
    echo "   Backend failed to start"
    journalctl -u lunchtogether-backend -n 50
    exit 1
fi

# Deploy Frontend
echo "3. Deploying frontend..."
cd $APP_DIR/frontend

# Install dependencies
echo "   - Installing dependencies..."
sudo -u $APP_USER npm ci --production=false

# Build frontend
echo "   - Building frontend..."
sudo -u $APP_USER npm run build

# Set proper permissions
chown -R $APP_USER:www-data $APP_DIR/frontend/dist
chmod -R 755 $APP_DIR/frontend/dist

# Reload nginx
echo "   - Reloading nginx..."
nginx -t && systemctl reload nginx

echo ""
echo "Deployment complete!"
echo "  - Backend: systemctl status lunchtogether-backend"
echo "  - Logs: journalctl -u lunchtogether-backend -f"
