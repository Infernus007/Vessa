#!/bin/bash

# Database Configuration (Defaults - Override in production!)
export DB_USER=${DB_USER:-vessa}
export DB_PASSWORD=${DB_PASSWORD:-password123}
export DB_HOST=${DB_HOST:-localhost}
export DB_PORT=${DB_PORT:-3306}
export DB_NAME=${DB_NAME:-vessa}

# Redis Configuration
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}

# Rate Limiting Configuration
export RATE_LIMIT=${RATE_LIMIT:-true}
export RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
export RATE_LIMIT_PERIOD=${RATE_LIMIT_PERIOD:-3600}

# Start the server using Gunicorn (Production)
# Use poetry run if running locally, or just gunicorn if in Docker/venv
if command -v poetry &> /dev/null; then
    echo "Starting with Poetry..."
    poetry run gunicorn -c gunicorn.conf.py main:app
else
    echo "Starting with Gunicorn..."
    gunicorn -c gunicorn.conf.py main:app
fi