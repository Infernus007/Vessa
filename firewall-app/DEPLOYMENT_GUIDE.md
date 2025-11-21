# VESSA Deployment Guide

This guide covers how to deploy VESSA in a production environment.

## Prerequisites

- Docker & Docker Compose (v2.0+)
- A domain name (for SSL)
- A server with at least 2GB RAM (4GB recommended for ML models)

## 1. Environment Configuration

Create a `.env` file in the `firewall-app` directory based on `env.example`.
**CRITICAL:** Change the following values for production:

```bash
ENVIRONMENT=production
DEBUG=false
DB_PASSWORD=<generate_secure_password>
JWT_SECRET_KEY=<generate_secure_key>
# Generate key: openssl rand -hex 32
```

## 2. Docker Deployment (Recommended)

We provide a production-ready `docker-compose.yml` in the root directory.

1. **Build and Start:**
   ```bash
   # From project root
   docker-compose up -d --build
   ```

2. **Verify Status:**
   ```bash
   docker-compose ps
   docker-compose logs -f backend
   ```

## 3. Nginx Reverse Proxy

For SSL termination and rate limiting, use the provided Nginx configuration.

1. **Install Nginx:**
   ```bash
   sudo apt update
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure Nginx:**
   Copy `firewall-app/nginx.conf` to `/etc/nginx/sites-available/vessa`.
   ```bash
   sudo cp firewall-app/nginx.conf /etc/nginx/sites-available/vessa
   sudo ln -s /etc/nginx/sites-available/vessa /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Setup SSL (Let's Encrypt):**
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```

## 4. Database Migrations

Run migrations to set up the database schema:

```bash
# Using Docker
docker-compose exec backend poetry run alembic upgrade head
```

## 5. Monitoring & Maintenance

- **Logs:**
  - Backend: `docker-compose logs -f backend`
  - Nginx: `/var/log/nginx/vessa_access.log`
  
- **Backups:**
  - Backup your `.env` file.
  - Backup MySQL data volume: `docker run --rm --volumes-from vessa-db-1 -v $(pwd):/backup ubuntu tar cvf /backup/backup.tar /var/lib/mysql`

## Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'absolution'"**
- Ensure you are building from the project root, NOT inside `firewall-app`.
- Correct: `docker-compose build` (from root)
- Incorrect: `docker build .` (inside `firewall-app`)

**Issue: Database connection failed**
- Check `DB_HOST` is set to `db` (Docker service name) or `localhost` (if running locally).
- Verify passwords match in `.env` and `docker-compose.yml`.
