#!/bin/bash

# Function to check if required environment variables are set
check_required_vars() {
    local required_vars=("DB_NAME" "DB_USER" "DB_PASSWORD" "DB_HOST" "DB_PORT")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "Error: Required environment variables are not set: ${missing_vars[*]}"
        exit 1
    fi
}

# Check required environment variables
check_required_vars

# Wait for postgres
echo "Waiting for postgres at $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL started"

# Wait for Redis if REDIS_HOST is set
if [ ! -z "$REDIS_HOST" ]; then
    echo "Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
        echo "Redis is unavailable - sleeping"
        sleep 1
    done
    echo "Redis started"
fi

# Create necessary directories with proper permissions
mkdir -p /app/staticfiles /app/media/posters /app/logs
chmod -R 777 /app/staticfiles /app/media /app/logs

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Download movie poster if it doesn't exist
if [ ! -f /app/media/posters/loneliness_runner_1962.jpg ]; then
    echo "Downloading movie poster..."
    mkdir -p /app/media/posters
    wget -O /app/media/posters/loneliness_runner_1962.jpg https://m.media-amazon.com/images/M/MV5BZTk1ZWQ1NzUtOWE2NC00ZjNhLTkzZjUtYWNjZmYwNjQ5OWE2XkEyXkFqcGdeQXVyMTIyNzY1NzM@._V1_.jpg
    chmod 644 /app/media/posters/loneliness_runner_1962.jpg
fi

# Load initial data if needed
echo "Loading initial data..."
python manage.py loaddata movies/fixtures/initial_movies.json || true

# Create superuser if needed
echo "Creating superuser if needed..."
python manage.py createsuperuser --noinput || true

# Start the application
echo "Starting application..."
exec "$@" 