# Firewall App Backend

A FastAPI/Flask-based backend service that integrates with the Absolution ML package to provide real-time malicious request detection and classification.

## Features

- Real-time request analysis
- RESTful API endpoints
- Integration with Absolution ML models
- Request logging and monitoring
- Rate limiting and security features
- Swagger/OpenAPI documentation

## API Endpoints

### Request Analysis

```http
POST /api/v1/analyze
Content-Type: application/json

{
    "method": "POST",
    "path": "/api/login",
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0..."
    },
    "body": "{\"username\": \"admin\", \"password\": \"password123\"}"
}
```

Response:
```json
{
    "is_malicious": true,
    "attack_type": "sql_injection",
    "confidence": 0.95,
    "ood_score": 0.02,
    "timestamp": "2024-03-14T12:00:00Z"
}
```

### Health Check

```http
GET /api/v1/health
```

Response:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "model_status": "loaded"
}
```

## Development Setup

1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Required environment variables:
   DB_USER=vessa
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=vessa
   REDIS_URL=redis://localhost:6379/0
   RATE_LIMIT=true
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_PERIOD=3600
   ```

4. Start the development server:
   ```bash
   # Using the start script
   ./start_server.sh
   
   # Or directly with Poetry
  poetry run uvicorn main:app --host 0.0.0.0 --port 8000
 ├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core application logic
│   ├── models/        # Data models
│   └── services/      # Business logic services
├── tests/             # Test suite
├── Dockerfile         # Docker configuration
├── pyproject.toml     # Project dependencies
├── start_server.sh    # Development server script
└── README.md         # This file
```

## Configuration

The application can be configured using environment variables:

### Database Configuration
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_NAME`: Database name

### Redis Configuration
- `REDIS_URL`: Redis connection URL

### Rate Limiting
- `RATE_LIMIT`: Enable/disable rate limiting
- `RATE_LIMIT_REQUESTS`: Number of requests allowed
- `RATE_LIMIT_PERIOD`: Time period in seconds

### Other Configuration
- `MODEL_PATH`: Path to the ML model files
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `API_KEY`: API key for authentication

## Testing

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details 