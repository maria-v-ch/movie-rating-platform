#!/bin/bash

set -e  # Exit on any error

echo "Running CI checks in Docker..."

# Export required environment variables
export SECRET_KEY="django-insecure-test-key-for-development"
export DB_NAME="postgres"
export DB_USER="postgres"
export DB_PASSWORD="test_password"
export DB_PORT="5432"
export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_EMAIL="admin@example.com"
export DJANGO_SUPERUSER_PASSWORD="admin_password"
export GRAFANA_ADMIN_PASSWORD="admin"
export TEST_DB_PASSWORD="test_password"
export DEBUG="False"

# Clean up any existing containers
docker-compose -f docker-compose.ci.yml down -v
docker-compose -f docker-compose.ci.yml rm -fsv

# Run code quality checks in Docker
echo "Running code quality checks..."
docker-compose -f docker-compose.ci.yml run --rm web bash -c "
    pip install black isort flake8 pylint mypy coverage &&
    echo 'Running black...' &&
    black . &&
    echo 'Running isort...' &&
    isort . --profile black &&
    echo 'Running checks...' &&
    isort --check-only . &&
    black --check . &&
    echo 'Running flake8...' &&
    flake8 &&
    echo 'Running pylint...' &&
    pylint --django-settings-module=config.settings movies users reviews &&
    echo 'Running mypy...' &&
    mypy . &&
    echo 'Running tests with coverage...' &&
    coverage run manage.py test &&
    coverage report &&
    coverage report -m
"

# Clean up after checks
docker-compose -f docker-compose.ci.yml down -v

echo "CI checks completed!"
echo "Note: Some checks might show warnings or non-critical errors"
echo "Review the output above for any issues that need attention" 