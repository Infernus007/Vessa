# Database and Cache Setup Guide for VESSA Platform

This guide provides comprehensive instructions for setting up the MySQL database and Redis cache for the VESSA platform.

## Prerequisites

- MySQL Server installed
- Redis Server installed
- Python virtual environment set up
- Required Python packages installed

## Redis Setup

### Installation
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server  # Enable on boot

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### Rate Limiting Configuration

The platform uses Redis for rate limiting API requests. Default configuration:

```bash
RATE_LIMIT=true                    # Enable/disable rate limiting
RATE_LIMIT_REQUESTS=100           # Default requests per window
RATE_LIMIT_PERIOD=3600           # Default window period in seconds (1 hour)
REDIS_URL=redis://localhost:6379/0  # Redis connection URL
```

#### Custom Rate Limits
You can manage rate limits for specific API keys using the CLI:

```bash
# Set custom rate limits
python cli.py api set-limits <API_KEY> --requests 200 --window 7200

# View current rate limits
python cli.py api get-limits <API_KEY>
```

Rate limit headers in responses:
- X-RateLimit-Limit: Maximum requests allowed
- X-RateLimit-Remaining: Remaining requests in current window
- X-RateLimit-Reset: Timestamp when the limit resets
- X-RateLimit-Window: Time window in seconds

## Database Configuration

### MySQL Server Setup

1. Install MySQL Server (if not already installed)
2. Create a dedicated database and user:
   ```sql
   CREATE DATABASE vessa;
   CREATE USER 'vessa'@'localhost' IDENTIFIED BY 'password123';
   GRANT ALL PRIVILEGES ON vessa.* TO 'vessa'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Environment Variables

The following environment variables are used for configuration:

```bash
# Database Configuration
DB_USER=vessa
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=3306
DB_NAME=vessa

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

These can be set:
- Temporarily in the terminal before running commands
- In your `.env` file
- In your system's environment variables

### Database URL Format

The database URL is constructed using the following format:
```
mysql://[username]:[password]@[host]:[port]/[database_name]
```

### Database Management Using CLI

The platform provides a powerful CLI tool (`cli.py`) for managing the database, users, incidents, and API keys.

#### Database Commands

1. Initialize/Create Database Schema:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py db init
   ```

2. Drop All Tables (Warning: Destructive):
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py db drop
   ```

3. Full Database Reset (Drop + Create):
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py db setup
   ```

#### User Management Commands

1. Create a New User:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py user create
   ```

2. Create System User (for automated reporting):
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py user create-system-user
   ```

#### API Key Management Commands

1. Create API Key:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py api create --user-id <USER_ID> --name "Key Description"
   ```

2. List User's API Keys:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py api list --user-id <USER_ID>
   ```

3. Regenerate API Key:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py api regenerate <KEY_ID> --user-id <USER_ID>
   ```

4. Delete API Key:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py api delete <KEY_ID> --user-id <USER_ID>
   ```

#### Incident Management Commands

1. Create Incident:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py incident create
   ```

2. List Incidents:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py incident list
   ```

3. Update Incident:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py incident update <INCIDENT_ID> --status <STATUS> --severity <SEVERITY>
   ```

### Database Schema Updates

When making changes to the database schema:

1. Stop any running instances of the application
2. Back up your data if needed
3. Update the model definitions in `services/common/models/`
4. Run database setup to apply changes:
   ```bash
   DB_USER=vessa DB_PASSWORD=password123 DB_HOST=localhost DB_PORT=3306 DB_NAME=vessa python cli.py db setup
   ```

### Important Notes

1. Always use environment variables for database configuration
2. Store API keys securely - they cannot be retrieved after creation
3. The system user (system@vessa.internal) is used for automated incident reporting
4. Each incident is associated with the API key that reported it
5. Users can only access incidents related to their API keys

### Troubleshooting

1. If you see bcrypt version warnings, they can be safely ignored
2. For permission errors, ensure your MySQL user has proper privileges
3. For connection errors, verify your environment variables and MySQL server status

## Database Connection Details

The database connection is managed in `services/common/database/session.py` with the following features:

- Connection pooling enabled
- Pool size: 5 connections
- Max overflow: 10 connections
- Connection recycling: Every 1 hour
- Connection timeout: 30 seconds
- Health checks enabled (pool_pre_ping)

## Best Practices

1. Never commit sensitive database or Redis credentials
2. Use environment variables for configuration
3. Regularly backup the database
4. Monitor connection pool usage
5. Keep MySQL server and client libraries updated
6. Monitor Redis memory usage
7. Configure Redis persistence if needed
8. Set appropriate rate limits based on API usage patterns

## Support

For any database or cache-related issues, please:
1. Check MySQL server logs
2. Check Redis server logs (usually in /var/log/redis/redis-server.log)
3. Verify environment variables
4. Ensure all required packages are installed
5. Check for any firewall or network restrictions
6. Verify Redis connectivity using redis-cli
7. Monitor rate limiting headers in API responses 