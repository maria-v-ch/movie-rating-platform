#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Clear previous coverage data
coverage erase

# Run tests with coverage and save output
coverage run --source=. manage.py test movies.tests.test_models movies.tests.test_api movies.tests.test_views movies.tests.test_view_internals movies.tests.test_security movies.tests.test_performance reviews.tests.test_api -v 2 > test_output.txt 2>&1

# Generate coverage report and append to output
coverage report >> test_output.txt 2>&1 