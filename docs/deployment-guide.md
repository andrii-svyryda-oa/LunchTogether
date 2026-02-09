# Deployment Guide

## Overview

LunchTogether is deployed to a VPS (Virtual Private Server) running Ubuntu 22.04 LTS with:
- **Nginx** as a reverse proxy with SSL termination
- **Systemd** for backend service management
- **PostgreSQL** as the database
- **GitHub Actions** for automated CI/CD

## Initial Server Setup

### 1. Purchase a VPS

**Recommended providers:**
| Provider       | Cost/Month | Notes                    |
|----------------|------------|--------------------------|
| Hetzner        | $7-15      | Best value, EU-based     |
| DigitalOcean   | $12-24     | Good documentation       |
| Linode         | $12-24     | Reliable                 |
| Vultr          | $12-24     | Wide region coverage     |
| AWS Lightsail  | $12-20     | AWS ecosystem            |

**Minimum specs:** 2 CPU cores, 4GB RAM, 40GB SSD
**Recommended specs:** 4 CPU cores, 8GB RAM, 80GB SSD

### 2. Configure DNS Records

Add the following DNS records for your domain:

| Type | Name  | Value            |
|------|-------|------------------|
| A    | @     | `<server-ip>`    |
| A    | www   | `<server-ip>`    |

### 3. Connect to the Server

```bash
ssh root@your-server-ip
```

### 4. Clone the Repository

```bash
cd /var/www
git clone <repository-url> lunchtogether
cd lunchtogether
```

### 5. Run the Setup Script

```bash
chmod +x infrastructure/setup.sh
./infrastructure/setup.sh <domain> <db_password> <jwt_secret> [sentry_dsn] <ssl_email>
```

**Parameters:**
| Parameter     | Description                        | Example                      |
|---------------|------------------------------------|------------------------------|
| `domain`      | Your domain name                   | `lunchtogether.com`          |
| `db_password` | PostgreSQL password                | *(use a strong password)*    |
| `jwt_secret`  | JWT signing secret                 | *(use a random 64-char key)* |
| `sentry_dsn`  | Sentry DSN (optional, use `''`)    | `''`                         |
| `ssl_email`   | Email for SSL certificate          | `admin@lunchtogether.com`    |

**Example:**
```bash
./infrastructure/setup.sh lunchtogether.com "MyStr0ngP@ss!" "$(openssl rand -hex 32)" '' admin@lunchtogether.com
```

The setup script will:
1. Install Python 3.12, Node.js 20, PostgreSQL 16, Nginx, Certbot, and uv
2. Create the application user and directories
3. Set up the PostgreSQL database
4. Configure Nginx with SSL
5. Create systemd service for the backend
6. Configure the firewall (UFW)
7. Set up log rotation
8. Configure automated SSL renewal and database backups

### 6. Deploy the Application

```bash
sudo ./infrastructure/deploy.sh
```

### 7. Verify the Installation

```bash
# Check backend service
sudo systemctl status lunchtogether-backend

# Check nginx
sudo systemctl status nginx

# Test the health endpoint
curl https://yourdomain.com/api/health

# Check SSL certificate
sudo certbot certificates
```

## Manual Deployment

When you need to deploy manually (without CI/CD):

```bash
# SSH into server
ssh user@your-server

# Deploy
cd /var/www/lunchtogether
sudo ./infrastructure/deploy.sh
```

The deploy script will:
1. Pull the latest code from git
2. Install backend dependencies and run migrations
3. Restart the backend service
4. Install frontend dependencies and build
5. Reload nginx

## Automated Deployment via GitHub Actions

### Configure GitHub Secrets

Go to your GitHub repository -> **Settings** -> **Secrets and variables** -> **Actions**, and add:

| Secret             | Description                             |
|--------------------|-----------------------------------------|
| `SSH_PRIVATE_KEY`  | Private SSH key for server access       |
| `SERVER_HOST`      | Server IP address or hostname           |
| `SERVER_USER`      | SSH username (usually `root` or sudo user) |
| `DOMAIN`           | Your domain name (for health checks)    |

### Generate SSH Key for GitHub Actions

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions" -f github_actions_key

# Copy the public key to the server
ssh-copy-id -i github_actions_key.pub user@your-server

# The private key content goes into the SSH_PRIVATE_KEY secret
cat github_actions_key
```

### Trigger a Deployment

Deployments happen automatically when you push to the `main` branch. You can also trigger a manual deployment from the **Actions** tab using the "Run workflow" button.

### Monitor Deployments

Go to your GitHub repository -> **Actions** tab to view:
- CI pipeline status (runs on every push and PR)
- Deployment pipeline status (runs on push to `main`)

## Monitoring and Maintenance

### View Logs

```bash
# Backend service logs (live)
sudo journalctl -u lunchtogether-backend -f

# Backend logs (last 100 lines)
sudo journalctl -u lunchtogether-backend -n 100

# Backend logs (since 1 hour ago)
sudo journalctl -u lunchtogether-backend --since "1 hour ago"

# Nginx access log
sudo tail -f /var/www/lunchtogether/logs/nginx-access.log

# Nginx error log
sudo tail -f /var/www/lunchtogether/logs/nginx-error.log
```

### Service Management

```bash
# Restart backend
sudo systemctl restart lunchtogether-backend

# Stop backend
sudo systemctl stop lunchtogether-backend

# Start backend
sudo systemctl start lunchtogether-backend

# Check status
sudo systemctl status lunchtogether-backend

# Reload nginx (after config changes)
sudo nginx -t && sudo systemctl reload nginx
```

## Backup and Restore

### Database Backups

Automated daily backups are configured via cron (runs at 2:00 AM daily). Backups are stored in `/var/backups/lunchtogether/` with 30-day retention.

```bash
# Manual backup
sudo /usr/local/bin/backup-lunchtogether-db

# List backups
ls -lh /var/backups/lunchtogether/
```

### Restore from Backup

```bash
# Restore (will stop backend, restore DB, and restart backend)
sudo ./infrastructure/scripts/restore-db.sh /var/backups/lunchtogether/lunchtogether_20260210_020000.sql.gz
```

## SSL Certificate Management

SSL certificates are managed by Let's Encrypt (Certbot) with automatic renewal via cron.

```bash
# Check certificate status
sudo certbot certificates

# Manual renewal
sudo certbot renew

# Test renewal (dry run)
sudo certbot renew --dry-run
```

## Security Checklist

- [ ] SSH key authentication is set up (disable password auth)
- [ ] No passwords or secrets in the repository
- [ ] Database password is strong and unique
- [ ] JWT secret is a random 64+ character key
- [ ] Firewall only allows ports 22, 80, 443
- [ ] Nginx security headers are configured
- [ ] File upload size is limited
- [ ] PostgreSQL is not accessible from the internet
- [ ] Regular database backups are running
- [ ] SSL certificate auto-renewal is working

## Performance Tuning

### Backend Workers

The number of uvicorn workers should be: `(2 x CPU_CORES) + 1`

| CPU Cores | Workers |
|-----------|---------|
| 2         | 5       |
| 4         | 9       |

Edit the systemd service to adjust:
```bash
sudo systemctl edit lunchtogether-backend
```

### PostgreSQL

For a server with 4GB+ RAM, edit `/etc/postgresql/16/main/postgresql.conf`:

```ini
shared_buffers = 256MB        # 25% of RAM
effective_cache_size = 1GB    # 50-75% of RAM
maintenance_work_mem = 64MB
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```
