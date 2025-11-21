FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r vessa && useradd -r -g vessa vessa

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy poetry files
COPY firewall-app/pyproject.toml firewall-app/poetry.lock ./

# Copy the absolution package (assumes build context is project root)
# Copy the absolution package to /absolution (matching ../absolution from /app)
COPY absolution /absolution

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the application code
COPY firewall-app .

# Change ownership to non-root user
RUN chown -R vessa:vessa /app

# Switch to non-root user
USER vessa

# Expose the port
EXPOSE 8000

# Command to run the application (Production)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]