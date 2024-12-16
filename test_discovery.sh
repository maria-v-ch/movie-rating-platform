#!/bin/bash

echo "1. Running movies tests..."
python manage.py test movies.tests.test_models movies.tests.test_api movies.tests.test_views movies.tests.test_performance movies.tests.test_security --verbosity 2

echo "2. Running reviews tests..."
python manage.py test reviews.tests.test_api --verbosity 2

echo "3. Running users tests..."
python manage.py test users.tests.test_models users.tests.test_views users.tests.test_forms --verbosity 2

echo "Test discovery complete." 