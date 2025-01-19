# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev

# Install Python dependencies
COPY requirements/base.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r base.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Create app user
RUN useradd -m -U app_user && \
    mkdir -p /home/app_user

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and requirements from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/base.txt requirements.txt

# Install Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --find-links=/wheels -r requirements.txt

# Create necessary directories and set permissions
RUN mkdir -p /app/media/posters /app/logs /app/staticfiles && \
    chown -R app_user:app_user /app && \
    chmod -R 755 /app && \
    chmod g+s /app/logs /app/media/posters /app/staticfiles && \
    chmod 777 /app/logs /app/media/posters /app/staticfiles

# Create health check script
RUN echo '#!/bin/bash\n\
echo "[$(date)] Running health check..."\n\
\n\
# Check if any Django management command is running\n\
if ps aux | grep -q "[p]ython manage.py"; then\n\
    echo "Django management command is running, health check passes"\n\
    exit 0\n\
fi\n\
\n\
# Check if Gunicorn is running\n\
if ! ps aux | grep -q "[g]unicorn.*config.wsgi:application"; then\n\
    echo "Gunicorn is not running"\n\
    exit 1\n\
fi\n\
\n\
# Check health endpoint\n\
echo "Checking health endpoint..."\n\
if curl -s -f http://localhost:8080/health/ > /dev/null; then\n\
    echo "Health endpoint is responding"\n\
    exit 0\n\
else\n\
    echo "Health endpoint failed to respond"\n\
    exit 1\n\
fi' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Copy project files
COPY --chown=app_user:app_user . .

# Copy and set up entrypoint
COPY --chown=app_user:app_user entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to app user
USER app_user

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]