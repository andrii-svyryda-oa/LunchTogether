# Local Development Guide

## Prerequisites

Before getting started, make sure you have the following installed:

- **Python 3.12** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **PostgreSQL 16** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/)

## Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd lunchtogether

# Make scripts executable
chmod +x infrastructure/scripts/*.sh

# Run the local setup script
./infrastructure/scripts/setup-local.sh
```

The setup script will:
1. Verify all prerequisites are installed
2. Install `uv` (Python package manager) if needed
3. Set up the backend (virtual environment, dependencies, `.env` file)
4. Set up the frontend (npm dependencies, `.env` file)
5. Create the PostgreSQL database and user
6. Run database migrations

## Running the Application

### Option A: Using VSCode (Recommended)

1. Open the project in VSCode
2. Install recommended extensions when prompted (or manually from `.vscode/extensions.json`)
3. Press **F5** to start debugging the full stack (starts both backend and frontend)
4. Or use **Ctrl+Shift+P** -> **"Tasks: Run Task"** to run individual tasks:
   - `Backend: Start` - Start the backend server
   - `Frontend: Start` - Start the frontend dev server
   - `Start All Services` - Start both backend and frontend

### Option B: Using Terminal Scripts

```bash
# Terminal 1: Start backend
./infrastructure/scripts/start-backend.sh

# Terminal 2: Start frontend
./infrastructure/scripts/start-frontend.sh
```

### Application URLs

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000         |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |

## Database Management

### Create a New Migration

```bash
cd backend
uv run alembic revision --autogenerate -m "Description of the migration"
```

Or use the VSCode task: **Ctrl+Shift+P** -> **"Tasks: Run Task"** -> **"Backend: Create Migration"**

### Run Migrations

```bash
cd backend
uv run alembic upgrade head
```

### Rollback a Migration

```bash
cd backend
uv run alembic downgrade -1
```

### View Migration History

```bash
cd backend
uv run alembic history
```

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=app --cov-report=html -v

# Run a specific test file
uv run pytest tests/test_auth.py -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm run test
```

## Linting and Formatting

### Backend (Ruff)

```bash
cd backend

# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .
```

### Frontend (ESLint + Prettier)

```bash
cd frontend

# Run ESLint
npm run lint

# Type check
npm run type-check
```

## Adding Dependencies

### Backend

```bash
cd backend

# Add a runtime dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>
```

### Frontend

```bash
cd frontend

# Add a runtime dependency
npm install <package-name>

# Add a development dependency
npm install --save-dev <package-name>
```

## Accessing the Database Directly

```bash
# Connect to the local database
psql -U lunchtogether -d lunchtogether -h localhost
```

## Environment Variables

### Backend (`backend/.env`)

| Variable                         | Description                    | Default (Local)                     |
|----------------------------------|--------------------------------|-------------------------------------|
| `DATABASE_URL`                   | PostgreSQL connection string   | `postgresql+asyncpg://lunchtogether:lunchtogether_dev@localhost:5432/lunchtogether` |
| `JWT_SECRET_KEY`                 | Secret key for JWT tokens      | `dev-secret-key-change-in-production` |
| `JWT_ALGORITHM`                  | JWT algorithm                  | `HS256`                             |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`| Token expiration time          | `30`                                |
| `UPLOAD_DIR`                     | File upload directory          | `./uploads`                         |
| `MAX_UPLOAD_SIZE`                | Max upload size (bytes)        | `10485760` (10MB)                   |
| `SENTRY_DSN`                     | Sentry DSN (optional)          | *(empty)*                           |
| `CORS_ORIGINS`                   | Allowed CORS origins           | `["http://localhost:3000"]`         |
| `ENVIRONMENT`                    | Environment name               | `development`                       |

### Frontend (`frontend/.env`)

| Variable             | Description         | Default (Local)                |
|----------------------|---------------------|--------------------------------|
| `VITE_API_BASE_URL`  | Backend API URL     | `http://localhost:8000/api`    |
| `VITE_APP_NAME`      | Application name    | `LunchTogether`                |

## Troubleshooting

### PostgreSQL is not running

```bash
# Linux
sudo systemctl start postgresql

# macOS (Homebrew)
brew services start postgresql@16

# Windows
net start postgresql-x64-16
```

### Port already in use

```bash
# Find process on port 8000 (backend)
lsof -i :8000
# Or on Windows:
netstat -ano | findstr :8000

# Find process on port 3000 (frontend)
lsof -i :3000
```

### Migration conflicts

```bash
cd backend

# Check current migration state
uv run alembic current

# If there are conflicts, you may need to:
uv run alembic stamp head  # Mark current DB as up-to-date
uv run alembic revision --autogenerate -m "Resolve conflicts"
```
