#!/bin/bash
set -e

# Parameters
DOMAIN=${1:-""}
DB_PASSWORD=${2:-""}
JWT_SECRET=${3:-""}
SENTRY_DSN=${4:-""}
SSL_EMAIL=${5:-""}
REPO_URL=${6:-""}

# Validate required parameters
if [ -z "$DOMAIN" ] || [ -z "$DB_PASSWORD" ] || [ -z "$JWT_SECRET" ] || [ -z "$SSL_EMAIL" ] || [ -z "$REPO_URL" ]; then
    echo "Usage: ./setup.sh <domain> <db_password> <jwt_secret> <sentry_dsn|''> <ssl_email> <repo_url>"
    echo "Example: ./setup.sh lunchtogether.com 'dbpass123' 'jwtsecret123' '' admin@lunchtogether.com https://github.com/org/LunchTogether.git"
    exit 1
fi

# Configuration
APP_USER="lunchtogether"
APP_DIR="/var/www/lunchtogether"
UPLOAD_DIR="/var/www/lunchtogether/uploads"
DB_NAME="lunchtogether"
DB_USER="lunchtogether"
SECRETS_DIR="/etc/lunchtogether"

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
export PATH="$HOME/.local/bin:$PATH"

# Create application user
echo "9. Creating application user..."
sudo useradd -m -s /bin/bash $APP_USER || true
sudo usermod -aG www-data $APP_USER

# Install uv for app user
echo "10. Installing uv for application user..."
sudo -u $APP_USER bash << 'EOF'
set -e
export UV_INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$UV_INSTALL_DIR"
curl -LsSf https://astral.sh/uv/install.sh | sh
EOF

# Create application directory and clone repo
echo "11. Creating application directories and cloning repository..."
sudo mkdir -p "$(dirname "$APP_DIR")"
sudo chown "$APP_USER":www-data "$(dirname "$APP_DIR")"

sudo mkdir -p "$APP_DIR/logs"
sudo mkdir -p "$UPLOAD_DIR"
sudo chown -R "$APP_USER":www-data "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"

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
# Note: we must use `tee`, not `sudo -u ... cat > file`, because the `>` redirect
# is evaluated by the caller's shell, not by sudo. Using cat + redirect would
# write the file as the invoking user (often root) with default permissions
# and leak the secrets below to anyone who can read /var/www/lunchtogether.
echo "13. Creating environment configuration..."
sudo -u "$APP_USER" tee "$APP_DIR/backend/.env" > /dev/null << EOF
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
sudo chown "$APP_USER":"$APP_USER" "$APP_DIR/backend/.env"
sudo chmod 600 "$APP_DIR/backend/.env"

# Setup Nginx
echo "14. Configuring Nginx..."
sudo cp $APP_DIR/infrastructure/nginx/lunchtogether.conf /etc/nginx/sites-available/lunchtogether
sudo sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/lunchtogether
sudo sed -i "s|APP_DIR_PLACEHOLDER|$APP_DIR|g" /etc/nginx/sites-available/lunchtogether
sudo ln -sf /etc/nginx/sites-available/lunchtogether /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Chicken-and-egg: our nginx config references /etc/letsencrypt/live/$DOMAIN/*.pem,
# but Certbot hasn't run yet, so those files don't exist -> `nginx -t` fails ->
# nginx won't start -> Certbot can't do its HTTP-01 challenge.
# Workaround: drop a short-lived self-signed cert at the expected path so nginx
# can boot. Nginx loads certs into memory on start, so we can delete the file on
# disk later without disturbing the running process. Certbot will then write the
# real Let's Encrypt cert at the same path and a reload will pick it up.
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
if [ ! -s "$CERT_DIR/fullchain.pem" ] || [ ! -s "$CERT_DIR/privkey.pem" ]; then
    echo "   Generating temporary self-signed cert for $DOMAIN..."
    sudo mkdir -p "$CERT_DIR"
    sudo openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout "$CERT_DIR/privkey.pem" \
        -out "$CERT_DIR/fullchain.pem" \
        -subj "/CN=$DOMAIN" >/dev/null 2>&1
fi

# Webroot for the ACME HTTP-01 challenge (nginx HTTP block serves this path)
sudo mkdir -p /var/www/certbot

# Test nginx configuration
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Setup SSL with Certbot
echo "15. Setting up SSL certificate..."
# Remove the dummy cert dir so Certbot writes a clean live/ with proper symlinks
# into archive/. Nginx keeps running because the dummy cert is already loaded
# into the running process's memory. Don't `nginx -t` or reload between here
# and the certbot call below, or you'll get BIO_new_file errors.
sudo rm -rf "/etc/letsencrypt/live/$DOMAIN" \
            "/etc/letsencrypt/archive/$DOMAIN" \
            "/etc/letsencrypt/renewal/$DOMAIN.conf"

# Use the `webroot` authenticator (not `--nginx`) because `--nginx` runs
# `nginx -t` as a pre-check, which fails while the cert paths are missing.
# Webroot just needs nginx to serve /.well-known/acme-challenge from
# /var/www/certbot, which our HTTP server block already does.
sudo certbot certonly --webroot -w /var/www/certbot \
    -d "$DOMAIN" -d "www.$DOMAIN" \
    --non-interactive --agree-tos -m "$SSL_EMAIL"

# Real cert is now in place; reload nginx to load it.
sudo nginx -t
sudo systemctl reload nginx

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
# Note: `sudo cat > /path` only elevates `cat`; the `>` redirect runs as the
# caller and fails with "Permission denied" on /etc/logrotate.d. Use `sudo tee`.
echo "18. Setting up log rotation..."
sudo tee /etc/logrotate.d/lunchtogether > /dev/null << EOF
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
# Write the DB password to a root-only secrets file instead of sed-replacing it
# into a world-readable script in /usr/local/bin. Using `tee` so the redirect
# runs with elevated privileges.
sudo mkdir -p "$SECRETS_DIR"
sudo chmod 700 "$SECRETS_DIR"
printf 'PGPASSWORD=%s\n' "$DB_PASSWORD" | sudo tee "$SECRETS_DIR/backup.env" > /dev/null
sudo chmod 600 "$SECRETS_DIR/backup.env"
sudo chown root:root "$SECRETS_DIR/backup.env"

sudo install -m 0755 "$APP_DIR/infrastructure/scripts/backup-db.sh" /usr/local/bin/backup-lunchtogether-db
(sudo crontab -l 2>/dev/null || true; echo "0 2 * * * /usr/local/bin/backup-lunchtogether-db") | sudo crontab -

echo ""
echo "Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the first deploy:   cd $APP_DIR && sudo ./infrastructure/deploy.sh"
echo "2. Verify the app:          https://$DOMAIN"
echo "3. Verify health endpoint:  curl https://$DOMAIN/api/health"
echo ""
echo "Useful commands:"
echo "  - View backend logs: sudo journalctl -u lunchtogether-backend -f"
echo "  - View nginx logs: sudo tail -f $APP_DIR/logs/nginx-error.log"
echo "  - Restart backend: sudo systemctl restart lunchtogether-backend"
echo "  - Check backend status: sudo systemctl status lunchtogether-backend"
