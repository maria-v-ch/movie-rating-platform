#!/bin/sh

# Function to wait for a service
wait_for_service() {
    host="$1"
    port="$2"
    service_name="$3"
    echo "Waiting for $service_name at $host:$port..."
    
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    
    echo "$service_name started"
}

# Wait for PostgreSQL
wait_for_service "db" "5432" "PostgreSQL"

# Wait for Redis
wait_for_service "redis" "6379" "Redis"

# Ensure directories exist with correct permissions
for dir in "/app/logs" "/app/media/posters" "/app/staticfiles"; do
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        install -d -m 755 -o app_user -g app_user "$dir"
    fi
done

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Load initial data
echo "Loading initial data..."
python manage.py loaddata initial_movies.json || true

# Create superuser if needed
echo "Creating superuser if needed..."
python manage.py createsuperuser --noinput || true

echo "Starting application..."
exec "$@"