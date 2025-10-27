"""CLI tools for VESSA Platform.

This module provides command-line tools for managing the VESSA Platform,
including database operations, user management, and incident management.
"""

import os
import sys
import click
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import secrets
import string
import asyncio
import redis
import json

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from services.common.models import Base  # Import from common models package
from services.user.core.user_service import UserService
from services.incident.core.incident_service import IncidentService
from services.common.database.session import get_database_url
from services.common.config import Settings

def get_db_session():
    """Create a new database session."""
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

@click.group()
def cli():
    """VESSA Platform management tools."""
    pass

@cli.group()
def db():
    """Database management commands."""
    pass

@db.command()
def init():
    """Initialize the database schema using Alembic migrations."""
    try:
        import subprocess
        
        # Run Alembic upgrade to head
        result = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        click.echo("✅ Database migrations applied successfully!")
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error applying migrations: {e.stderr}", err=True)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

@db.command()
def drop():
    """Drop all database tables using SQLAlchemy metadata."""
    if click.confirm("⚠️ This will delete all data. Are you sure?", abort=True):
        try:
            engine = create_engine(get_database_url())
            
            # Use SQLAlchemy's metadata to drop all tables safely
            # This prevents SQL injection and handles dependencies correctly
            Base.metadata.drop_all(bind=engine)
                
            click.echo("✅ Database tables dropped successfully!")
        except Exception as e:
            click.echo(f"❌ Error dropping database tables: {str(e)}", err=True)

@db.command()
def setup():
    """Initialize database and create all tables using migrations."""
    try:
        import subprocess
        
        # Drop existing tables
        engine = create_engine(get_database_url())
        Base.metadata.drop_all(bind=engine)
        click.echo("✅ Dropped existing tables")
        
        # Run migrations
        result = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        click.echo("✅ Database initialized successfully!")
        click.echo(result.stdout)
        
    except Exception as e:
        click.echo(f"❌ Error setting up database: {str(e)}", err=True)

@db.command()
def migrate():
    """Create a new migration based on model changes."""
    try:
        import subprocess
        
        message = click.prompt("Migration message", type=str)
        
        result = subprocess.run(
            ["poetry", "run", "alembic", "revision", "--autogenerate", "-m", message],
            capture_output=True,
            text=True,
            check=True
        )
        
        click.echo("✅ Migration created successfully!")
        click.echo(result.stdout)
        
    except Exception as e:
        click.echo(f"❌ Error creating migration: {str(e)}", err=True)

@db.command()
def upgrade():
    """Apply pending migrations."""
    try:
        import subprocess
        
        result = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        click.echo("✅ Migrations applied successfully!")
        click.echo(result.stdout)
        
    except Exception as e:
        click.echo(f"❌ Error applying migrations: {str(e)}", err=True)

@db.command()
def downgrade():
    """Rollback the last migration."""
    if click.confirm("⚠️ This will rollback the last migration. Continue?", abort=True):
        try:
            import subprocess
            
            result = subprocess.run(
                ["poetry", "run", "alembic", "downgrade", "-1"],
                capture_output=True,
                text=True,
                check=True
            )
            
            click.echo("✅ Migration rolled back successfully!")
            click.echo(result.stdout)
            
        except Exception as e:
            click.echo(f"❌ Error rolling back migration: {str(e)}", err=True)

@db.command()
def history():
    """Show migration history."""
    try:
        import subprocess
        
        result = subprocess.run(
            ["poetry", "run", "alembic", "history", "--verbose"],
            capture_output=True,
            text=True,
            check=True
        )
        
        click.echo(result.stdout)
        
    except Exception as e:
        click.echo(f"❌ Error showing history: {str(e)}", err=True)

@cli.group()
def user():
    """User management commands."""
    pass

@user.command()
@click.option('--email', prompt=True, help='User email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='User password')
@click.option('--name', prompt=True, help='User name')
def create(email, password, name):
    """Create a new user."""
    db = get_db_session()
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(
            email=email,
            password=password,
            name=name,
        )
        click.echo(f"✅ User created successfully!")
        click.echo(f"ID: {user.id}")
        click.echo(f"Email: {user.email}")
    except IntegrityError:
        click.echo("❌ Error: Email already exists", err=True)
    except Exception as e:
        click.echo(f"❌ Error creating user: {str(e)}", err=True)
    finally:
        db.close()

@user.command()
def create_system_user():
    """Create the system user for automated incident reporting."""
    db = get_db_session()
    user_service = UserService(db)
    
    try:
        # Check if system user already exists
        if user_service.get_user_by_email("system@vessa.internal"):
            click.echo("✅ System user already exists!")
            return
            
        # Create system user with a secure random password
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        user = user_service.create_user(
            email="system@vessa.internal",
            password=password,
            name="VESSA System",
        )
        click.echo(f"✅ System user created successfully!")
        click.echo(f"ID: {user.id}")
        click.echo(f"Email: {user.email}")
    except Exception as e:
        click.echo(f"❌ Error creating system user: {str(e)}", err=True)
    finally:
        db.close()

@cli.group()
def incident():
    """Incident management commands."""
    pass

@incident.command()
@click.option('--title', prompt=True, help='Incident title')
@click.option('--description', prompt=True, help='Incident description')
@click.option('--severity', type=click.Choice(['low', 'medium', 'high', 'critical']), prompt=True, help='Incident severity')
@click.option('--reporter-id', prompt=True, help='ID of the user reporting the incident')
@click.option('--assigned-to', help='ID of the user to assign the incident to')
@click.option('--tags', help='Comma-separated list of tags')
def create(title, description, severity, reporter_id, assigned_to, tags):
    """Create a new security incident."""
    db = get_db_session()
    incident_service = IncidentService(db)
    
    try:
        incident = incident_service.create_incident(
            title=title,
            description=description,
            severity=severity,
            reporter_id=reporter_id,
            assigned_to=assigned_to,
            tags=tags.split(',') if tags else None
        )
        click.echo(f"✅ Incident created successfully!")
        click.echo(f"ID: {incident.id}")
        click.echo(f"Title: {incident.title}")
        click.echo(f"Severity: {incident.severity}")
        click.echo(f"Status: {incident.status}")
    except Exception as e:
        click.echo(f"❌ Error creating incident: {str(e)}", err=True)
    finally:
        db.close()

@incident.command()
@click.argument('incident_id')
@click.option('--status', type=click.Choice(['open', 'investigating', 'contained', 'resolved', 'closed']))
@click.option('--severity', type=click.Choice(['low', 'medium', 'high', 'critical']))
@click.option('--assigned-to', help='ID of the user to assign the incident to')
@click.option('--resolution-notes', help='Notes about incident resolution')
def update(incident_id, status, severity, assigned_to, resolution_notes):
    """Update an existing incident."""
    db = get_db_session()
    incident_service = IncidentService(db)
    
    try:
        incident = incident_service.update_incident(
            incident_id=incident_id,
            status=status,
            severity=severity,
            assigned_to=assigned_to,
            resolution_notes=resolution_notes
        )
        click.echo(f"✅ Incident updated successfully!")
        click.echo(f"ID: {incident.id}")
        click.echo(f"Title: {incident.title}")
        click.echo(f"Status: {incident.status}")
        click.echo(f"Severity: {incident.severity}")
        if incident.assigned_to:
            click.echo(f"Assigned to: {incident.assigned_to}")
    except Exception as e:
        click.echo(f"❌ Error updating incident: {str(e)}", err=True)
    finally:
        db.close()

@incident.command()
@click.option('--status', help='Filter by status')
@click.option('--severity', help='Filter by severity')
@click.option('--tag', help='Filter by tag')
@click.option('--page', type=int, default=1, help='Page number')
@click.option('--page-size', type=int, default=20, help='Items per page')
def list(status, severity, tag, page, page_size):
    """List security incidents."""
    db = get_db_session()
    incident_service = IncidentService(db)
    
    try:
        incidents = incident_service.list_incidents(
            page=page,
            page_size=page_size,
            status=status,
            severity=severity,
            tag=tag
        )
        
        if not incidents["items"]:
            click.echo("No incidents found.")
            return
            
        click.echo(f"Found {incidents['total']} incident(s):")
        for incident in incidents["items"]:
            click.echo("─" * 50)
            click.echo(f"ID: {incident.id}")
            click.echo(f"Title: {incident.title}")
            click.echo(f"Status: {incident.status}")
            click.echo(f"Severity: {incident.severity}")
            click.echo(f"Created: {incident.created_at}")
            if incident.tags:
                click.echo(f"Tags: {', '.join(incident.tags)}")
    except Exception as e:
        click.echo(f"❌ Error listing incidents: {str(e)}", err=True)
    finally:
        db.close()

@cli.group()
def api():
    """API key management commands."""
    pass

@api.command()
@click.option('--user-id', prompt=True, help='User ID to create key for')
@click.option('--name', prompt=True, help='Name/description for the API key')
@click.option('--expires-in-days', type=int, help='Optional number of days until key expires')
def create(user_id, name, expires_in_days):
    """Create a new API key for a user."""
    db = get_db_session()
    user_service = UserService(db)
    
    try:
        # Run the async function in the event loop
        api_key = asyncio.run(user_service.create_api_key(
            user_id=user_id,
            name=name,
            expires_in_days=expires_in_days
        ))
        click.echo("✅ API key created successfully!")
        click.echo("─" * 50)
        click.echo(f"Key ID: {api_key.id}")
        click.echo(f"Key: {api_key.key}")
        click.echo("─" * 50)
        click.echo("⚠️ Store this key securely - it won't be shown again!")
    except Exception as e:
        click.echo(f"❌ Error creating API key: {str(e)}", err=True)
    finally:
        db.close()

@api.command()
@click.argument('key_id')
@click.option('--user-id', prompt=True, help='User ID who owns the key')
def regenerate(key_id, user_id):
    """Regenerate an API key."""
    db = get_db_session()
    user_service = UserService(db)
    
    try:
        api_key = user_service.regenerate_api_key(key_id, user_id)
        click.echo("✅ API key regenerated successfully!")
        click.echo("─" * 50)
        click.echo(f"Key ID: {api_key.id}")
        click.echo(f"New Key: {api_key.key}")
        click.echo("─" * 50)
        click.echo("⚠️ Store this key securely - it won't be shown again!")
    except Exception as e:
        click.echo(f"❌ Error regenerating API key: {str(e)}", err=True)
    finally:
        db.close()

@api.command()
@click.argument('key_id')
@click.option('--user-id', prompt=True, help='User ID who owns the key')
def delete(key_id, user_id):
    """Delete an API key."""
    db = get_db_session()
    user_service = UserService(db)
    
    try:
        user_service.delete_api_key(key_id, user_id)
        click.echo("✅ API key deleted successfully!")
    except Exception as e:
        click.echo(f"❌ Error deleting API key: {str(e)}", err=True)
    finally:
        db.close()

@api.command()
@click.option('--user-id', prompt=True, help='User ID to list keys for')
def list(user_id):
    """List all API keys for a user."""
    db = get_db_session()
    user_service = UserService(db)
    
    try:
        keys = user_service.list_user_api_keys(user_id)
        if not keys:
            click.echo("No API keys found.")
            return
            
        click.echo(f"Found {len(keys)} API key(s):")
        for key in keys:
            click.echo("─" * 50)
            click.echo(f"ID: {key.id}")
            click.echo(f"Created: {key.created_at}")
            click.echo(f"Last Used: {key.last_used_at or 'Never'}")
            click.echo(f"Status: {'Active' if key.is_active else 'Inactive'}")
    except Exception as e:
        click.echo(f"❌ Error listing API keys: {str(e)}", err=True)
    finally:
        db.close()

@api.command()
@click.argument('api_key')
@click.option('--requests', type=int, required=True, help='Maximum requests allowed in the time window')
@click.option('--window', type=int, required=True, help='Time window in seconds')
def set_limits(api_key, requests, window):
    """Set custom rate limits for an API key."""
    try:
        settings = Settings()
        redis_client = redis.from_url(settings.redis_url)
        
        limits = {
            "max_requests": requests,
            "window_seconds": window
        }
        
        key = f"custom_limits:{api_key}"
        redis_client.set(key, json.dumps(limits))
        
        click.echo(f"✅ Rate limits set successfully for API key: {api_key}")
        click.echo(f"Max requests: {requests}")
        click.echo(f"Time window: {window} seconds")
    except Exception as e:
        click.echo(f"❌ Error setting rate limits: {str(e)}", err=True)

@api.command()
@click.argument('api_key')
def get_limits(api_key):
    """Get current rate limits for an API key."""
    try:
        settings = Settings()
        redis_client = redis.from_url(settings.redis_url)
        
        key = f"custom_limits:{api_key}"
        limits = redis_client.get(key)
        
        if limits:
            limits = json.loads(limits)
            click.echo(f"📊 Current rate limits for API key: {api_key}")
            click.echo(f"Max requests: {limits['max_requests']}")
            click.echo(f"Time window: {limits['window_seconds']} seconds")
        else:
            click.echo(f"ℹ️ Using default rate limits for API key: {api_key}")
            click.echo(f"Max requests: {settings.rate_limit_requests}")
            click.echo(f"Time window: {settings.rate_limit_period} seconds")
    except Exception as e:
        click.echo(f"❌ Error getting rate limits: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 