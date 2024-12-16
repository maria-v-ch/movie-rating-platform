#!/bin/bash

# Wait for postgres
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for postgres..."
  sleep 1
done

echo "PostgreSQL started"

# Create necessary directories with proper permissions
mkdir -p /app/staticfiles /app/media/posters /app/logs
chmod -R 777 /app/staticfiles /app/media /app/logs

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Download movie poster if it doesn't exist
if [ ! -f /app/media/posters/loneliness_runner_1962.jpg ]; then
    echo "Downloading movie poster..."
    mkdir -p /app/media/posters
    wget -O /app/media/posters/loneliness_runner_1962.jpg https://m.media-amazon.com/images/M/MV5BZTk1ZWQ1NzUtOWE2NC00ZjNhLTkzZjUtYWNjZmYwNjQ5OWE2XkEyXkFqcGdeQXVyMTIyNzY1NzM@._V1_.jpg
    chmod 644 /app/media/posters/loneliness_runner_1962.jpg
fi

# Load initial data if needed
python manage.py loaddata movies/fixtures/initial_movies.json || true

# Create superuser if needed
python manage.py createsuperuser --noinput || true

exec "$@" 