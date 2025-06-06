#!/bin/bash

# Database Configuration
export DB_USER=vessa
export DB_PASSWORD=password123
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=vessa

# Redis Configuration
export REDIS_URL=redis://localhost:6379/0

# Rate Limiting Configuration
export RATE_LIMIT=true
export RATE_LIMIT_REQUESTS=100
export RATE_LIMIT_PERIOD=3600

# Start the server using Poetry
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000 