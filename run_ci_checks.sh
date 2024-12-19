#!/bin/bash

set -e  # Exit on any error

echo "Running CI checks locally..."

# 1. Check Python version
echo "Checking Python version..."
python3 --version

# 2. Check pip dependencies
echo "Checking pip dependencies..."
pip install -r requirements.txt

# 3. Run code quality checks
echo "Running code quality checks..."
echo "Running isort..."
isort --check-only .
echo "Running black..."
black --check .
echo "Running flake8..."
flake8
echo "Running pylint..."
pylint --django-settings-module=config.settings movies users reviews
echo "Running mypy..."
mypy .

# 4. Run tests with coverage
echo "Running tests with coverage..."
coverage run manage.py test
coverage report
coverage report -m

echo "CI checks completed!"
echo "Note: Some checks might show warnings or non-critical errors"
echo "Review the output above for any issues that need attention" 