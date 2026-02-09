#!/bin/bash
set -e

# Parameters
DOMAIN=${1:-""}
DB_PASSWORD=${2:-""}
JWT_SECRET=${3:-""}
SENTRY_DSN=${4:-""}
SSL_EMAIL=${5:-""}

# Validate required parameters
if [ -z "$DOMAIN" ] || [ -z "$DB_PASSWORD" ] || [ -z "$JWT_SECRET" ] || [ -z "$SSL_EMAIL" ]; then
    echo "Usage: ./setup.sh <domain> <db_password> <jwt_secret> [sentry_dsn] <ssl_email>"
    echo "Example: ./setup.sh lunchtogether.com dbpass123 jwtsecret123 '' admin@lunchtogether.com"
    exit 1
fi

# Configuration
APP_USER="lunchtogether"
APP_DIR="/var/www/lunchtogether"
UPLOAD_DIR="/var/www/lunchtogether/uploads"
DB_NAME="lunchtogether"
DB_USER="lunchtogether"

echo "Setting up LunchTogether on VPS..."

# Update system
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "2. Installing required packages..."
sudo apt install -y \
    software-properties-common \
    build-essential \
    git \
    curl \
    wget

# Install Python 3.12
echo "3. Installing Python 3.12..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip

# Set Python 3.12 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Install Node.js 20
echo "4. Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
echo "5. Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
echo "6. Installing Nginx..."
sudo apt install -y nginx

# Install Certbot
echo "7. Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Install uv (Python package manager)
echo "8. Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Create application user
echo "9. Creating application user..."
sudo useradd -m -s /bin/bash $APP_USER || true
sudo usermod -aG www-data $APP_USER

# Install uv for app user
echo "10. Installing uv for application user..."
sudo -u $APP_USER bash << EOF
curl -LsSf https://astral.sh/uv/install.sh | sh
EOF

# Create application directory
echo "11. Creating application directories..."
sudo mkdir -p $APP_DIR/{backend,frontend,logs}
sudo mkdir -p $UPLOAD_DIR
sudo chown -R $APP_USER:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Setup PostgreSQL
echo "12. Setting up PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Configure PostgreSQL to allow local connections
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
sudo systemctl restart postgresql
sudo systemctl enable postgresql

# Create .env file
echo "13. Creating environment configuration..."
sudo -u $APP_USER cat > $APP_DIR/backend/.env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# JWT
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=$UPLOAD_DIR
MAX_UPLOAD_SIZE=10485760

# Sentry
SENTRY_DSN=$SENTRY_DSN

# CORS
CORS_ORIGINS=["https://$DOMAIN","https://www.$DOMAIN"]

# Environment
ENVIRONMENT=production
EOF

# Setup Nginx
echo "14. Configuring Nginx..."
sudo cp $APP_DIR/infrastructure/nginx/lunchtogether.conf /etc/nginx/sites-available/lunchtogether
sudo sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/lunchtogether
sudo sed -i "s|APP_DIR_PLACEHOLDER|$APP_DIR|g" /etc/nginx/sites-available/lunchtogether
sudo ln -sf /etc/nginx/sites-available/lunchtogether /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Setup SSL with Certbot
echo "15. Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $SSL_EMAIL --redirect

# Setup systemd services
echo "16. Creating systemd services..."
sudo cp $APP_DIR/infrastructure/systemd/lunchtogether-backend.service /etc/systemd/system/
sudo sed -i "s|APP_DIR_PLACEHOLDER|$APP_DIR|g" /etc/systemd/system/lunchtogether-backend.service
sudo sed -i "s|APP_USER_PLACEHOLDER|$APP_USER|g" /etc/systemd/system/lunchtogether-backend.service
sudo systemctl daemon-reload
sudo systemctl enable lunchtogether-backend

# Setup firewall
echo "17. Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Setup log rotation
echo "18. Setting up log rotation..."
sudo cat > /etc/logrotate.d/lunchtogether << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $APP_USER $APP_USER
    sharedscripts
}
EOF

# Setup cron job for SSL renewal
echo "19. Setting up SSL certificate auto-renewal..."
(sudo crontab -l 2>/dev/null || true; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | sudo crontab -

# Setup cron job for database backup
echo "20. Setting up automated database backups..."
sudo cp $APP_DIR/infrastructure/scripts/backup-db.sh /usr/local/bin/backup-lunchtogether-db
sudo chmod +x /usr/local/bin/backup-lunchtogether-db
sudo sed -i "s|DB_PASSWORD_PLACEHOLDER|$DB_PASSWORD|g" /usr/local/bin/backup-lunchtogether-db
(sudo crontab -l 2>/dev/null || true; echo "0 2 * * * /usr/local/bin/backup-lunchtogether-db") | sudo crontab -

echo ""
echo "Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository to $APP_DIR"
echo "2. Deploy your application using: cd $APP_DIR && sudo ./infrastructure/deploy.sh"
echo "3. The application will be available at: https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  - View backend logs: sudo journalctl -u lunchtogether-backend -f"
echo "  - View nginx logs: sudo tail -f $APP_DIR/logs/nginx-error.log"
echo "  - Restart backend: sudo systemctl restart lunchtogether-backend"
echo "  - Check backend status: sudo systemctl status lunchtogether-backend"
