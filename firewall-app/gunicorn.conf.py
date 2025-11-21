"""Gunicorn configuration for VESSA production deployment.

This file configures Gunicorn for production use with Uvicorn workers.
"""

import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes
# Recommended: (2 x num_cores) + 1
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests
max_requests_jitter = 50  # Add randomness to avoid all workers restarting at once

# Timeout
timeout = 300  # 5 minutes for long-running ML inference
keepalive = 120  # Keep connections alive for 2 minutes
graceful_timeout = 30  # Graceful shutdown timeout

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # - means stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")   # - means stdout
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "vessa-firewall"

# Server mechanics
daemon = False  # Don't daemonize (let systemd handle this)
pidfile = os.getenv("GUNICORN_PID_FILE", "/tmp/vessa-gunicorn.pid")
user = None  # Run as current user (systemd will set this)
group = None
umask = 0
tmp_upload_dir = None

# Preload application code before worker processes are forked
# This saves RAM and ensures app loads successfully before forking
preload_app = True

# Restart workers when code changes (development only)
reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print(f"[{proc_name}] Starting Gunicorn with {workers} workers")

def when_ready(server):
    """Called just after the server is started."""
    print(f"[{proc_name}] Server is ready. Listening on: {bind}")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"[{proc_name}] Worker {worker.pid} booted")
