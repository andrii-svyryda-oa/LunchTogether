# Deployment Implementation Plan

## Overview
This plan outlines the implementation of deployment infrastructure for local development and VPS production deployment. The setup uses direct installations of Python, Node.js, and PostgreSQL with systemd services, nginx as a reverse proxy with SSL, and GitHub Actions for CI/CD.

## Technology Stack
- VPS Server (Ubuntu 22.04 LTS recommended)
- Python 3.12 with uv
- Node.js 20+
- PostgreSQL 16
- Nginx (reverse proxy and static file serving)
- Certbot (SSL certificate management)
- Systemd (service management)
- GitHub Actions (CI/CD)

## Project Structure

```
lunchtogether/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI pipeline (lint, test, build)
│       └── deploy.yml              # Deployment pipeline
├── .vscode/
│   ├── launch.json                 # VSCode debug configurations
│   ├── tasks.json                  # VSCode tasks
│   └── settings.json               # VSCode workspace settings
├── deployment/
│   ├── setup.sh                    # One-time server setup script
│   ├── deploy.sh                   # Deployment script (called by CI/CD)
│   ├── nginx/
│   │   └── lunchtogether.conf      # Nginx configuration template
│   ├── systemd/
│   │   └── lunchtogether-backend.service
│   └── scripts/
│       ├── backup-db.sh            # Database backup script
│       ├── restore-db.sh           # Database restore script
│       └── update-certs.sh         # SSL certificate renewal
├── scripts/
│   ├── setup-local.sh              # Local development setup
│   ├── start-backend.sh            # Start backend locally
│   └── start-frontend.sh           # Start frontend locally
├── .env.example                    # Example environment variables
└── .env.local.example              # Example local environment variables
```

## Implementation Steps

### Part 1: Local Development Setup

#### 1. VSCode Launch Configuration
**Task**: Create VSCode debug configurations

**File to create**: `.vscode/launch.json`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend: Debug",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload"
      ],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "console": "integratedTerminal",
      "justMyCode": false,
      "gevent": false
    },
    {
      "name": "Backend: Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "-v",
        "-s"
      ],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Frontend: Debug Chrome",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    },
    {
      "name": "Frontend: Debug Edge",
      "type": "msedge",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ],
  "compounds": [
    {
      "name": "Full Stack: Debug",
      "configurations": [
        "Backend: Debug",
        "Frontend: Debug Chrome"
      ],
      "stopAll": true,
      "preLaunchTask": "Check Services"
    }
  ]
}
```

#### 2. VSCode Tasks Configuration
**Task**: Create VSCode tasks for common operations

**File to create**: `.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Backend: Install Dependencies",
      "type": "shell",
      "command": "uv sync",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Backend: Run Migrations",
      "type": "shell",
      "command": "uv run alembic upgrade head",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Backend: Create Migration",
      "type": "shell",
      "command": "uv run alembic revision --autogenerate -m \"${input:migrationName}\"",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Backend: Start",
      "type": "shell",
      "command": "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "build",
      "isBackground": true,
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": {
        "pattern": {
          "regexp": "^.*$",
          "file": 1,
          "location": 2,
          "message": 3
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": "Started server process",
          "endsPattern": "Application startup complete"
        }
      }
    },
    {
      "label": "Backend: Run Tests",
      "type": "shell",
      "command": "uv run pytest -v",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Backend: Run Tests with Coverage",
      "type": "shell",
      "command": "uv run pytest --cov=app --cov-report=html -v",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Backend: Lint (Ruff)",
      "type": "shell",
      "command": "uv run ruff check .",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Backend: Format (Ruff)",
      "type": "shell",
      "command": "uv run ruff format .",
      "options": {
        "cwd": "${workspaceFolder}/backend"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Frontend: Install Dependencies",
      "type": "shell",
      "command": "npm install",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Frontend: Start",
      "type": "shell",
      "command": "npm run dev",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "build",
      "isBackground": true,
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": {
        "pattern": {
          "regexp": "^.*$",
          "file": 1,
          "location": 2,
          "message": 3
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": "VITE.*ready in",
          "endsPattern": "Local:.*http://localhost:3000"
        }
      }
    },
    {
      "label": "Frontend: Build",
      "type": "shell",
      "command": "npm run build",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Frontend: Run Tests",
      "type": "shell",
      "command": "npm run test",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Frontend: Lint",
      "type": "shell",
      "command": "npm run lint",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Frontend: Type Check",
      "type": "shell",
      "command": "npm run type-check",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Check Services",
      "type": "shell",
      "command": "echo 'Checking if PostgreSQL is running...' && pg_isready || echo 'WARNING: PostgreSQL is not running!'",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Start All Services",
      "dependsOrder": "sequence",
      "dependsOn": [
        "Backend: Start",
        "Frontend: Start"
      ],
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ],
  "inputs": [
    {
      "id": "migrationName",
      "type": "promptString",
      "description": "Enter migration name",
      "default": "migration"
    }
  ]
}
```

#### 3. VSCode Workspace Settings
**Task**: Create recommended VSCode workspace settings

**File to create**: `.vscode/settings.json`

```json
{
  // Python settings
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "."
  ],
  "python.testing.unittestEnabled": false,
  "python.linting.enabled": false,
  
  // Ruff settings
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  
  // TypeScript/JavaScript settings
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[jsonc]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  
  // ESLint settings
  "eslint.workingDirectories": [
    "./frontend"
  ],
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  
  // File associations
  "files.associations": {
    "*.env.*": "dotenv",
    ".env.example": "dotenv"
  },
  
  // File exclusions
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true
  },
  
  "search.exclude": {
    "**/node_modules": true,
    "**/.venv": true,
    "**/dist": true,
    "**/build": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true
  },
  
  // Terminal settings
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "${workspaceFolder}/backend"
  },
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}/backend"
  },
  "terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder}/backend"
  },
  
  // Editor settings
  "editor.rulers": [88, 120],
  "editor.tabSize": 4,
  "[python]": {
    "editor.tabSize": 4
  },
  "[typescript]": {
    "editor.tabSize": 2
  },
  "[typescriptreact]": {
    "editor.tabSize": 2
  },
  "[javascript]": {
    "editor.tabSize": 2
  },
  "[json]": {
    "editor.tabSize": 2
  }
}
```

#### 4. VSCode Extensions Recommendations
**Task**: Create recommended extensions file

**File to create**: `.vscode/extensions.json`

```json
{
  "recommendations": [
    // Python
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    
    // JavaScript/TypeScript
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    
    // React
    "dsznajder.es7-react-js-snippets",
    
    // Database
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg",
    
    // Git
    "eamodio.gitlens",
    
    // Utilities
    "editorconfig.editorconfig",
    "mikestead.dotenv",
    "streetsidesoftware.code-spell-checker",
    "wayou.vscode-todo-highlight",
    
    // Tailwind CSS
    "bradlc.vscode-tailwindcss",
    
    // REST Client (optional)
    "humao.rest-client"
  ]
}
```

#### 5. Local Development Setup Script
**Task**: Create script to set up local development environment

**File to create**: `scripts/setup-local.sh`

```bash
#!/bin/bash
set -e

echo "Setting up local development environment..."

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 is not installed. Please install it first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install it first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first."
    exit 1
fi

# Install uv if not installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Setup backend
echo "Setting up backend..."
cd backend

# Create virtual environment and install dependencies
uv sync

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating backend .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://lunchtogether:lunchtogether_dev@localhost:5432/lunchtogether
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
SENTRY_DSN=
CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
EOF
fi

# Create uploads directory
mkdir -p uploads

cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend

# Install dependencies
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=LunchTogether
EOF
fi

cd ..

# Setup local PostgreSQL database
echo "Setting up PostgreSQL database..."
echo "Please enter your PostgreSQL superuser password when prompted."

# Create database and user
psql -U postgres << EOF
CREATE DATABASE lunchtogether;
CREATE USER lunchtogether WITH ENCRYPTED PASSWORD 'lunchtogether_dev';
GRANT ALL PRIVILEGES ON DATABASE lunchtogether TO lunchtogether;
ALTER DATABASE lunchtogether OWNER TO lunchtogether;
\c lunchtogether
GRANT ALL ON SCHEMA public TO lunchtogether;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Run migrations
echo "Running database migrations..."
cd backend
uv run alembic upgrade head
cd ..

echo ""
echo "✓ Local development environment is ready!"
echo ""
echo "To start the application:"
echo ""
echo "Option 1: Using VSCode"
echo "  - Open the project in VSCode"
echo "  - Press F5 to start debugging (starts both backend and frontend)"
echo "  - Or use 'Run Task' (Ctrl+Shift+P) to run individual tasks"
echo ""
echo "Option 2: Using terminal scripts"
echo "  1. Start backend: ./scripts/start-backend.sh"
echo "  2. Start frontend: ./scripts/start-frontend.sh"
echo ""
echo "URLs:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
```

#### 6. Backend Start Script
**Task**: Create script to start backend locally

**File to create**: `scripts/start-backend.sh`

```bash
#!/bin/bash
set -e

cd backend

echo "Starting backend server..."
echo "Backend will be available at: http://localhost:8000"
echo "API Docs will be available at: http://localhost:8000/docs"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start server with auto-reload
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. Frontend Start Script
**Task**: Create script to start frontend locally

**File to create**: `scripts/start-frontend.sh`

```bash
#!/bin/bash
set -e

cd frontend

echo "Starting frontend development server..."
echo "Frontend will be available at: http://localhost:3000"
echo ""

# Start development server
npm run dev
```

#### 8. Environment Files
**Task**: Create example environment files

**File to create**: `.env.example` (for production)

```env
# Database
DATABASE_URL=postgresql+asyncpg://lunchtogether:CHANGE_THIS_PASSWORD@localhost:5432/lunchtogether

# JWT
JWT_SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=/var/www/lunchtogether/uploads
MAX_UPLOAD_SIZE=10485760

# Sentry (optional)
SENTRY_DSN=

# CORS
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Environment
ENVIRONMENT=production
```

**File to create**: `.env.local.example`

```env
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://lunchtogether:lunchtogether_dev@localhost:5432/lunchtogether
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
SENTRY_DSN=
CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=LunchTogether
```

### Part 2: VPS Setup Scripts

#### 9. One-Time Setup Script
**Task**: Create comprehensive server setup script

**File to create**: `deployment/setup.sh`

**Script should accept parameters**:
- Domain name
- Database password
- JWT secret key
- Sentry DSN (optional)
- Email for SSL certificate

**Script implementation**:

```bash
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
sudo cp $APP_DIR/deployment/nginx/lunchtogether.conf /etc/nginx/sites-available/lunchtogether
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
sudo cp $APP_DIR/deployment/systemd/lunchtogether-backend.service /etc/systemd/system/
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
sudo cp $APP_DIR/deployment/scripts/backup-db.sh /usr/local/bin/backup-lunchtogether-db
sudo chmod +x /usr/local/bin/backup-lunchtogether-db
sudo sed -i "s|DB_PASSWORD_PLACEHOLDER|$DB_PASSWORD|g" /usr/local/bin/backup-lunchtogether-db
(sudo crontab -l 2>/dev/null || true; echo "0 2 * * * /usr/local/bin/backup-lunchtogether-db") | sudo crontab -

echo ""
echo "✓ Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository to $APP_DIR"
echo "2. Deploy your application using: cd $APP_DIR && ./deployment/deploy.sh"
echo "3. The application will be available at: https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  - View backend logs: sudo journalctl -u lunchtogether-backend -f"
echo "  - View nginx logs: sudo tail -f $APP_DIR/logs/nginx-error.log"
echo "  - Restart backend: sudo systemctl restart lunchtogether-backend"
echo "  - Check backend status: sudo systemctl status lunchtogether-backend"
```

#### 10. Nginx Configuration
**Task**: Create nginx configuration template

**File to create**: `deployment/nginx/lunchtogether.conf`

```nginx
# Backend upstream
upstream backend {
    server 127.0.0.1:8000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;

    # SSL configuration (will be managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logging
    access_log APP_DIR_PLACEHOLDER/logs/nginx-access.log;
    error_log APP_DIR_PLACEHOLDER/logs/nginx-error.log;

    # Max upload size
    client_max_body_size 10M;

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Backend docs (optional, remove in production)
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Uploaded files
    location /uploads/ {
        alias APP_DIR_PLACEHOLDER/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend static files
    location / {
        root APP_DIR_PLACEHOLDER/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

#### 11. Backend Systemd Service
**Task**: Create systemd service for backend

**File to create**: `deployment/systemd/lunchtogether-backend.service`

```ini
[Unit]
Description=LunchTogether Backend Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=APP_USER_PLACEHOLDER
Group=www-data
WorkingDirectory=APP_DIR_PLACEHOLDER/backend
EnvironmentFile=APP_DIR_PLACEHOLDER/backend/.env

# Run migrations before starting
ExecStartPre=/home/APP_USER_PLACEHOLDER/.cargo/bin/uv run alembic upgrade head

# Start the application
ExecStart=/home/APP_USER_PLACEHOLDER/.cargo/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lunchtogether-backend

[Install]
WantedBy=multi-user.target
```

### Part 3: Deployment Scripts

#### 12. Deployment Script
**Task**: Create script for deploying updates

**File to create**: `deployment/deploy.sh`

```bash
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
    echo "   ✓ Backend is running"
else
    echo "   ✗ Backend failed to start"
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
echo "✓ Deployment complete!"
echo "  - Backend: systemctl status lunchtogether-backend"
echo "  - Logs: journalctl -u lunchtogether-backend -f"
```

#### 13. Database Backup Script
**Task**: Create database backup script

**File to create**: `deployment/scripts/backup-db.sh`

```bash
#!/bin/bash
set -e

BACKUP_DIR="/var/backups/lunchtogether"
DB_NAME="lunchtogether"
DB_USER="lunchtogether"
DB_PASSWORD="DB_PASSWORD_PLACEHOLDER"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lunchtogether_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
echo "Creating database backup..."
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# Set permissions
chmod 600 $BACKUP_FILE

# Delete old backups
find $BACKUP_DIR -name "lunchtogether_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "✓ Backup created: $BACKUP_FILE"
```

#### 14. Database Restore Script
**Task**: Create database restore script

**File to create**: `deployment/scripts/restore-db.sh`

```bash
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

echo "⚠️  This will restore the database from backup and overwrite current data!"
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

echo "✓ Database restored successfully!"
```

### Part 4: GitHub Actions CI/CD

#### 15. CI Pipeline
**Task**: Create CI pipeline for testing and building

**File to create**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-lint-test:
    name: Backend Lint & Test
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          export PATH="$HOME/.cargo/bin:$PATH"
          uv sync
      
      - name: Run ruff linting
        working-directory: ./backend
        run: |
          export PATH="$HOME/.cargo/bin:$PATH"
          uv run ruff check .
      
      - name: Run ruff formatting check
        working-directory: ./backend
        run: |
          export PATH="$HOME/.cargo/bin:$PATH"
          uv run ruff format --check .
      
      - name: Run tests
        working-directory: ./backend
        run: |
          export PATH="$HOME/.cargo/bin:$PATH"
          uv run pytest
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test
          JWT_SECRET_KEY: test-secret-key
          UPLOAD_DIR: /tmp/uploads

  frontend-lint-test:
    name: Frontend Lint & Test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: ./frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run ESLint
        working-directory: ./frontend
        run: npm run lint
      
      - name: Run TypeScript check
        working-directory: ./frontend
        run: npm run type-check
      
      - name: Run tests
        working-directory: ./frontend
        run: npm run test
      
      - name: Build
        working-directory: ./frontend
        run: npm run build
```

#### 16. Deployment Pipeline
**Task**: Create deployment pipeline with SSH

**File to create**: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.SERVER_HOST }} >> ~/.ssh/known_hosts
      
      - name: Deploy Application
        run: |
          ssh ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} << 'ENDSSH'
            set -e
            
            # Navigate to application directory
            cd /var/www/lunchtogether
            
            echo "Pulling latest code..."
            sudo -u lunchtogether git fetch origin
            sudo -u lunchtogether git reset --hard origin/main
            
            echo "Deploying backend..."
            cd backend
            sudo -u lunchtogether /home/lunchtogether/.cargo/bin/uv sync
            sudo -u lunchtogether /home/lunchtogether/.cargo/bin/uv run alembic upgrade head
            sudo systemctl restart lunchtogether-backend
            
            # Wait and check if backend started successfully
            sleep 3
            if ! systemctl is-active --quiet lunchtogether-backend; then
              echo "Backend failed to start!"
              sudo journalctl -u lunchtogether-backend -n 50
              exit 1
            fi
            
            echo "✓ Backend deployed successfully"
            
            echo "Deploying frontend..."
            cd ../frontend
            sudo -u lunchtogether npm ci --production=false
            sudo -u lunchtogether npm run build
            
            echo "Reloading nginx..."
            sudo nginx -t
            sudo systemctl reload nginx
            
            echo "✓ Frontend deployed successfully"
          ENDSSH
      
      - name: Health Check
        run: |
          sleep 5
          response=$(curl -s -o /dev/null -w "%{http_code}" https://${{ secrets.DOMAIN }}/api/health || true)
          if [ "$response" = "200" ]; then
            echo "✓ Health check passed"
          else
            echo "✗ Health check failed (HTTP $response)"
            exit 1
          fi
      
      - name: Notify Deployment
        if: always()
        run: |
          if [ "${{ job.status }}" = "success" ]; then
            echo "🚀 Deployment successful!"
          else
            echo "❌ Deployment failed!"
          fi
```

#### 17. GitHub Secrets Documentation
**Task**: Document required GitHub secrets

**Required GitHub Secrets**:
- `SSH_PRIVATE_KEY`: Private SSH key for server access
- `SERVER_HOST`: Server IP address or hostname
- `SERVER_USER`: SSH username (usually root or a sudo user)
- `DOMAIN`: Your domain name (for health checks)

**How to generate SSH key**:
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions" -f github_actions_key

# Copy the public key to the server
ssh-copy-id -i github_actions_key.pub user@your-server

# Add the private key content to GitHub Secrets as SSH_PRIVATE_KEY
cat github_actions_key
```

### Part 5: Documentation

#### 18. Local Development Guide
**Task**: Create local development documentation

**File to create**: `docs/local-development.md`

**Sections to include**:

1. **Prerequisites**
   - Python 3.12
   - Node.js 20+
   - PostgreSQL 16
   - Git

2. **Initial Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd lunchtogether
   
   # Run setup script
   chmod +x scripts/*.sh
   ./scripts/setup-local.sh
   ```

3. **Running the Application**
   
   **Option A: Using VSCode (Recommended)**
   ```
   - Open project in VSCode
   - Press F5 to start debugging (full stack)
   - Or use Ctrl+Shift+P -> "Tasks: Run Task"
     - "Backend: Start" - Start backend server
     - "Frontend: Start" - Start frontend dev server
     - "Start All Services" - Start both
   ```
   
   **Option B: Using Terminal Scripts**
   ```bash
   # Terminal 1: Start backend
   ./scripts/start-backend.sh
   
   # Terminal 2: Start frontend
   ./scripts/start-frontend.sh
   ```

4. **Database Management**
   ```bash
   # Create a new migration
   cd backend
   uv run alembic revision --autogenerate -m "Description"
   
   # Run migrations
   uv run alembic upgrade head
   
   # Rollback migration
   uv run alembic downgrade -1
   ```

5. **Common Tasks**
   - Running tests
   - Linting code
   - Adding dependencies
   - Accessing database directly

#### 19. Deployment Guide
**Task**: Create deployment documentation

**File to create**: `docs/deployment-guide.md`

**Sections to include**:

1. **Initial Server Setup**
   - Purchase VPS (Ubuntu 22.04 LTS)
   - Configure DNS records
   - Connect via SSH
   - Clone repository
   - Run setup script
   - Verify installation

2. **Manual Deployment**
   ```bash
   # SSH into server
   ssh user@your-server
   
   # Deploy application
   cd /var/www/lunchtogether
   sudo ./deployment/deploy.sh
   ```

3. **Automated Deployment via GitHub Actions**
   - Configure GitHub secrets
   - Push to main branch
   - Monitor deployment in Actions tab

4. **Monitoring and Maintenance**
   ```bash
   # View backend logs
   sudo journalctl -u lunchtogether-backend -f
   
   # View nginx logs
   sudo tail -f /var/www/lunchtogether/logs/nginx-error.log
   
   # Restart services
   sudo systemctl restart lunchtogether-backend
   sudo systemctl reload nginx
   
   # Check service status
   sudo systemctl status lunchtogether-backend
   ```

5. **Backup and Restore**
   ```bash
   # Manual backup
   sudo /usr/local/bin/backup-lunchtogether-db
   
   # Restore from backup
   sudo /var/www/lunchtogether/deployment/scripts/restore-db.sh /var/backups/lunchtogether/backup_file.sql.gz
   ```

6. **SSL Certificate Management**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Manual renewal (automatic renewal is set up via cron)
   sudo certbot renew
   
   # Test renewal
   sudo certbot renew --dry-run
   ```

#### 20. Operations Runbook
**Task**: Create operations guide

**File to create**: `docs/operations.md`

**Common Commands**:
```bash
# Service Management
sudo systemctl status lunchtogether-backend
sudo systemctl restart lunchtogether-backend
sudo systemctl stop lunchtogether-backend
sudo systemctl start lunchtogether-backend

# Logs
sudo journalctl -u lunchtogether-backend -f
sudo journalctl -u lunchtogether-backend -n 100
sudo journalctl -u lunchtogether-backend --since "1 hour ago"
sudo tail -f /var/www/lunchtogether/logs/nginx-access.log
sudo tail -f /var/www/lunchtogether/logs/nginx-error.log

# Database
sudo -u postgres psql -U lunchtogether -d lunchtogether
sudo -u lunchtogether psql -d lunchtogether

# Nginx
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl status nginx

# Disk Space
df -h
du -sh /var/www/lunchtogether/*
du -sh /var/backups/lunchtogether/*

# Process Management
ps aux | grep uvicorn
htop
```

**Troubleshooting Common Issues**:
1. Backend won't start
2. Database connection errors
3. Nginx 502 errors
4. SSL certificate issues
5. High memory usage
6. Disk space full

## Environment Variables Required

### Local Development

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql+asyncpg://lunchtogether:lunchtogether_dev@localhost:5432/lunchtogether
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
SENTRY_DSN=
CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
```

**Frontend** (`frontend/.env`):
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=LunchTogether
```

### Production

**Backend** (`/var/www/lunchtogether/backend/.env`):
```env
DATABASE_URL=postgresql+asyncpg://lunchtogether:STRONG_PASSWORD@localhost:5432/lunchtogether
JWT_SECRET_KEY=generate-a-strong-random-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=/var/www/lunchtogether/uploads
MAX_UPLOAD_SIZE=10485760
SENTRY_DSN=your-sentry-dsn-if-using
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
ENVIRONMENT=production
```

## Validation Checklist

### Local Development
- [ ] Python 3.12 is installed
- [ ] Node.js 20+ is installed
- [ ] PostgreSQL is running
- [ ] Setup script completes without errors
- [ ] VSCode configurations are created (.vscode/ folder)
- [ ] Backend starts on port 8000
- [ ] Frontend starts on port 3000
- [ ] Database migrations run successfully
- [ ] API documentation is accessible at /docs
- [ ] File uploads work correctly
- [ ] VSCode debugging works (F5)
- [ ] VSCode tasks work (Ctrl+Shift+P -> Run Task)
- [ ] Recommended extensions are installed

### Server Setup
- [ ] Setup script completes without errors
- [ ] PostgreSQL is running and database is created
- [ ] Nginx is running and serving default page
- [ ] SSL certificate is installed and valid
- [ ] Systemd service is created and enabled
- [ ] Firewall allows only necessary ports (22, 80, 443)
- [ ] Cron jobs are set up (SSL renewal, backups)
- [ ] Log rotation is configured

### Deployment
- [ ] GitHub Actions CI passes all tests
- [ ] Backend deploys successfully via SSH
- [ ] Frontend builds and deploys
- [ ] Backend service restarts without errors
- [ ] Nginx reloads successfully
- [ ] Health check endpoint returns 200
- [ ] SSL certificate is valid
- [ ] Application is accessible via HTTPS
- [ ] File uploads work on production
- [ ] Database migrations run automatically

### Security
- [ ] SSH key authentication is set up
- [ ] No passwords in repository
- [ ] Database password is strong and secure
- [ ] JWT secret is random and secure
- [ ] Firewall only allows necessary ports
- [ ] Nginx security headers are configured
- [ ] File upload size is limited
- [ ] Uploaded files have proper permissions
- [ ] PostgreSQL is not accessible from internet

## Cost Considerations

**VPS Requirements**:
- Minimum: 2 CPU cores, 4GB RAM, 40GB SSD (~$10-20/month)
- Recommended: 4 CPU cores, 8GB RAM, 80GB SSD (~$20-40/month)

**Additional Costs**:
- Domain name: ~$10-15/year
- SSL certificate: Free (Let's Encrypt)
- Sentry (optional): Free tier available

**Recommended VPS Providers**:
- DigitalOcean Droplet - $12-24/month
- Linode - $12-24/month
- Vultr - $12-24/month
- Hetzner - $7-15/month (best value, EU-based)
- AWS Lightsail - $12-20/month
- OVH - $7-15/month

## Next Steps After Implementation

1. **Local Development**:
   - Clone repository
   - Run setup script
   - Start backend and frontend
   - Verify everything works locally

2. **Server Setup**:
   - Purchase VPS
   - Set up DNS records (A record pointing to server IP)
   - SSH into server
   - Clone repository to `/var/www/lunchtogether`
   - Run setup script
   - Verify services are running

3. **Configure CI/CD**:
   - Generate SSH key for GitHub Actions
   - Add public key to server
   - Add secrets to GitHub repository
   - Push to main branch to trigger deployment

4. **Testing**:
   - Test all features in production
   - Verify SSL certificate
   - Test file uploads
   - Verify database backups are running
   - Test manual deployment script

5. **Monitoring**:
   - Set up Sentry error tracking (optional)
   - Configure uptime monitoring (UptimeRobot, Pingdom, etc.)
   - Set up log monitoring/alerting
   - Monitor disk space usage

6. **Optimization**:
   - Tune backend worker count based on server resources
   - Configure database connection pooling
   - Optimize nginx caching
   - Set up CDN for static assets (optional)

## Performance Tuning

### Backend (uvicorn workers)
```ini
# In systemd service file
ExecStart=/home/lunchtogether/.cargo/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
```

Number of workers: `(2 x CPU_CORES) + 1`
- 2 CPU cores: 5 workers
- 4 CPU cores: 9 workers

### PostgreSQL
```bash
# Edit /etc/postgresql/16/main/postgresql.conf
shared_buffers = 256MB  # 25% of RAM for 1GB, adjust accordingly
effective_cache_size = 1GB  # 50-75% of RAM
maintenance_work_mem = 64MB
```

### Nginx
Already configured with:
- Gzip compression
- Static file caching
- Connection keepalive
- Proper buffer sizes
