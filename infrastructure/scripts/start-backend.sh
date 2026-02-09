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
