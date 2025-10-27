"""Gunicorn configuration for VESSA production deployment.

This file configures Gunicorn for production use with Uvicorn workers.
"""

import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes
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

# SSL (if not using reverse proxy)
# Leave commented if using Nginx for SSL termination
# keyfile = "/path/to/privkey.pem"
# certfile = "/path/to/fullchain.pem"
# ssl_version = ssl.PROTOCOL_TLS
# cert_reqs = ssl.CERT_NONE
# do_handshake_on_connect = False
# ciphers = "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print(f"[{proc_name}] Starting Gunicorn with {workers} workers")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print(f"[{proc_name}] Reloading configuration")

def when_ready(server):
    """Called just after the server is started."""
    print(f"[{proc_name}] Server is ready. Listening on: {bind}")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"[{proc_name}] Worker {worker.pid} booted")

def pre_exec(server):
    """Called just before a new master process is forked."""
    print(f"[{proc_name}] Forking new master process")

def when_ready(server):
    """Called just after the server is started."""
    print(f"[{proc_name}] Server ready. Spawned {workers} workers")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    print(f"[{proc_name}] Worker {worker.pid} received INT/QUIT signal")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"[{proc_name}] Worker {worker.pid} aborted (timeout)")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug("%s %s" % (req.method, req.path))

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"[{proc_name}] Worker {worker.pid} exited")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"[{proc_name}] Worker {worker.pid} exiting")

def nworkers_changed(server, new_value, old_value):
    """Called when the number of workers changes."""
    print(f"[{proc_name}] Number of workers changed from {old_value} to {new_value}")

def on_exit(server):
    """Called just before the master process exits."""
    print(f"[{proc_name}] Master process exiting")

# Environment variables
raw_env = [
    f"ENVIRONMENT={os.getenv('ENVIRONMENT', 'production')}",
]

# Preload application code before worker processes are forked
# This can save RAM but makes code reloading harder
preload_app = False  # Set to True for memory savings in production

# Restart workers when code changes (development only)
reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"

# Spew configuration on startup
spew = False

# Enable check for alive workers
check_config = False

# Print configuration
print_config = False

