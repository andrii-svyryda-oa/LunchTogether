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
echo "Local development environment is ready!"
echo ""
echo "To start the application:"
echo ""
echo "Option 1: Using VSCode"
echo "  - Open the project in VSCode"
echo "  - Press F5 to start debugging (starts both backend and frontend)"
echo "  - Or use 'Run Task' (Ctrl+Shift+P) to run individual tasks"
echo ""
echo "Option 2: Using terminal scripts"
echo "  1. Start backend: ./infrastructure/scripts/start-backend.sh"
echo "  2. Start frontend: ./infrastructure/scripts/start-frontend.sh"
echo ""
echo "URLs:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
