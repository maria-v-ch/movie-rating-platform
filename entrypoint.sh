#!/bin/bash

# Wait for postgres
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for postgres..."
  sleep 1
done

echo "PostgreSQL started"

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Load initial data if needed
python manage.py loaddata movies/fixtures/initial_movies.json || true

# Create superuser if needed
python manage.py createsuperuser --noinput || true

exec "$@" 