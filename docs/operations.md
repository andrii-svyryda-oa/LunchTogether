# Operations Runbook

## Quick Reference

### Service Management

```bash
# Backend
sudo systemctl status lunchtogether-backend
sudo systemctl restart lunchtogether-backend
sudo systemctl stop lunchtogether-backend
sudo systemctl start lunchtogether-backend

# Nginx
sudo nginx -t                    # Test config before reloading
sudo systemctl reload nginx      # Reload config (no downtime)
sudo systemctl restart nginx     # Full restart
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

### Viewing Logs

```bash
# Backend service logs
sudo journalctl -u lunchtogether-backend -f              # Live tail
sudo journalctl -u lunchtogether-backend -n 100           # Last 100 lines
sudo journalctl -u lunchtogether-backend --since "1 hour ago"
sudo journalctl -u lunchtogether-backend --since "2026-01-15" --until "2026-01-16"

# Nginx logs
sudo tail -f /var/www/lunchtogether/logs/nginx-access.log
sudo tail -f /var/www/lunchtogether/logs/nginx-error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

### Database Operations

```bash
# Connect to database
sudo -u postgres psql -U lunchtogether -d lunchtogether

# Manual backup
sudo /usr/local/bin/backup-lunchtogether-db

# List backups
ls -lh /var/backups/lunchtogether/

# Restore from backup
sudo ./infrastructure/scripts/restore-db.sh /var/backups/lunchtogether/<backup_file>.sql.gz

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('lunchtogether'));"
```

### Disk Space

```bash
# Overall disk usage
df -h

# Application disk usage
du -sh /var/www/lunchtogether/*
du -sh /var/www/lunchtogether/uploads/
du -sh /var/backups/lunchtogether/

# Find large files
du -h /var/www/lunchtogether/ | sort -rh | head -20

# Clean old logs
sudo journalctl --vacuum-time=7d
```

### Process Management

```bash
# Check running uvicorn processes
ps aux | grep uvicorn

# System resource usage
htop

# Memory usage
free -h

# Network connections
ss -tlnp
```

## Troubleshooting

### 1. Backend Won't Start

**Symptoms:** `systemctl status lunchtogether-backend` shows `failed`

**Steps:**
```bash
# Check the error logs
sudo journalctl -u lunchtogether-backend -n 50

# Common causes:
# - Missing environment variables -> check /var/www/lunchtogether/backend/.env
# - Database connection failed -> check PostgreSQL is running
# - Port already in use -> check for orphan processes
# - Migration error -> run migrations manually

# Try running manually to see errors
cd /var/www/lunchtogether/backend
sudo -u lunchtogether /home/lunchtogether/.cargo/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000

# If port is in use
sudo lsof -i :8000
sudo kill <pid>
```

### 2. Database Connection Errors

**Symptoms:** Backend logs show `connection refused` or `authentication failed`

**Steps:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Restart PostgreSQL if needed
sudo systemctl restart postgresql

# Test connection
sudo -u postgres psql -U lunchtogether -d lunchtogether -c "SELECT 1;"

# Check pg_hba.conf for authentication settings
sudo cat /etc/postgresql/16/main/pg_hba.conf

# Check PostgreSQL is listening
ss -tlnp | grep 5432
```

### 3. Nginx 502 Bad Gateway

**Symptoms:** Users see "502 Bad Gateway" error page

**Steps:**
```bash
# Check if backend is running
sudo systemctl status lunchtogether-backend

# If not running, start it
sudo systemctl start lunchtogether-backend

# Check nginx error logs
sudo tail -20 /var/www/lunchtogether/logs/nginx-error.log

# Verify nginx config
sudo nginx -t

# Check if backend port is reachable
curl -s http://127.0.0.1:8000/api/health
```

### 4. SSL Certificate Issues

**Symptoms:** Browser shows certificate warning or HTTPS doesn't work

**Steps:**
```bash
# Check certificate status
sudo certbot certificates

# Manual renewal
sudo certbot renew

# If renewal fails, try standalone mode
sudo systemctl stop nginx
sudo certbot renew --standalone
sudo systemctl start nginx

# Test auto-renewal
sudo certbot renew --dry-run
```

### 5. High Memory Usage

**Symptoms:** Server is slow, OOM killer active

**Steps:**
```bash
# Check what's using memory
free -h
ps aux --sort=-%mem | head -10

# Check for memory leaks in backend
sudo journalctl -u lunchtogether-backend --since "1 hour ago" | grep -i memory

# Reduce uvicorn workers if needed (edit service file)
sudo systemctl edit lunchtogether-backend
# Override ExecStart with fewer workers

# Restart backend
sudo systemctl restart lunchtogether-backend

# Clear system caches (temporary relief)
sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches
```

### 6. Disk Space Full

**Symptoms:** Services fail, writes fail, "No space left on device"

**Steps:**
```bash
# Check disk usage
df -h

# Find largest directories
du -h / --max-depth=2 | sort -rh | head -20

# Clean old backups (keep last 7)
cd /var/backups/lunchtogether
ls -t | tail -n +8 | xargs rm -f

# Clean old journal logs
sudo journalctl --vacuum-time=3d

# Clean apt cache
sudo apt clean

# Clean old uploads if applicable
du -sh /var/www/lunchtogether/uploads/
```

### 7. Deployment Failed

**Symptoms:** GitHub Actions deployment fails

**Steps:**
```bash
# Check GitHub Actions logs in the repository Actions tab

# SSH into server and check manually
ssh user@your-server

# Check if git pull worked
cd /var/www/lunchtogether
git status
git log --oneline -5

# Try manual deployment
sudo ./infrastructure/deploy.sh

# Check backend service after manual deploy
sudo systemctl status lunchtogether-backend
sudo journalctl -u lunchtogether-backend -n 50
```

## Scheduled Tasks

| Schedule    | Task                       | Command/Location                              |
|-------------|----------------------------|-----------------------------------------------|
| Daily 2 AM  | Database backup            | `/usr/local/bin/backup-lunchtogether-db`      |
| Daily 3 AM  | SSL certificate renewal    | `certbot renew`                               |
| Daily       | Log rotation               | `/etc/logrotate.d/lunchtogether`              |

## Important File Locations

| Purpose                  | Path                                                 |
|--------------------------|------------------------------------------------------|
| Application root         | `/var/www/lunchtogether/`                            |
| Backend code             | `/var/www/lunchtogether/backend/`                    |
| Frontend build           | `/var/www/lunchtogether/frontend/dist/`              |
| Backend env file         | `/var/www/lunchtogether/backend/.env`                |
| Upload directory         | `/var/www/lunchtogether/uploads/`                    |
| Application logs         | `/var/www/lunchtogether/logs/`                       |
| Nginx site config        | `/etc/nginx/sites-available/lunchtogether`           |
| Systemd service          | `/etc/systemd/system/lunchtogether-backend.service`  |
| Database backups         | `/var/backups/lunchtogether/`                        |
| SSL certificates         | `/etc/letsencrypt/live/<domain>/`                    |
| Logrotate config         | `/etc/logrotate.d/lunchtogether`                     |

## Emergency Procedures

### Full Service Restart

```bash
sudo systemctl restart postgresql
sudo systemctl restart lunchtogether-backend
sudo systemctl reload nginx
```

### Rollback to Previous Deployment

```bash
cd /var/www/lunchtogether

# See recent commits
git log --oneline -10

# Rollback to a specific commit
sudo -u lunchtogether git checkout <commit-hash>

# Redeploy
sudo ./infrastructure/deploy.sh
```

### Restore Database from Backup

```bash
# Stop backend first
sudo systemctl stop lunchtogether-backend

# Find the backup to restore
ls -lh /var/backups/lunchtogether/

# Restore
sudo ./infrastructure/scripts/restore-db.sh /var/backups/lunchtogether/<backup_file>.sql.gz

# Backend will be restarted by the restore script
```
