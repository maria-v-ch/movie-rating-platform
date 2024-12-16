# Movie Rating Platform

A Django-based platform for rating and reviewing art-house films, similar to IMDb but focused on art cinema. The platform allows users to browse movies, leave reviews, and rate films while providing detailed information about art-house movements and cinematography.

## Features

- Browse and search art-house films by title, director, or movement
- User registration, authentication, and profile management
- Movie reviews with rating system
- Favorite movies functionality
- Detailed movie information including directors, cinematographers, and art movements
- Password reset functionality with email support
- Comprehensive admin interface for content management
- RESTful API with token authentication
- Real-time monitoring with Prometheus and Grafana
- Responsive web design with mobile support
- Automated testing with high coverage (>85%)

## Tech Stack

- Python 3.9
- Django 5.1
- Django REST Framework
- PostgreSQL 13
- Docker & Docker Compose
- Nginx
- Prometheus & Grafana
- GitHub Actions for CI/CD
- Bootstrap 5 for frontend

## Prerequisites

- Docker and Docker Compose
- Git
- Python 3.9+ (for local development)
- virtualenv (optional, for local development)

## Installation & Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd movie_rating_platform
```

2. Choose your setup method:

### A. Development Setup (recommended for local development)
```bash
# Copy development environment file
cp .env.development.sample .env

# Edit .env with your development settings

# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Create and load initial data (in another terminal)
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
docker-compose -f docker-compose.dev.yml exec web python manage.py loaddata movies/fixtures/initial_movies.json
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Access the development server at http://localhost:8000
```

### B. Production Setup
```bash
# Copy production environment file
cp .env.sample .env

# Edit .env with your production settings
# Make sure to set strong passwords and proper domain settings

# Copy and configure Nginx settings
cp paragoni.space.conf.sample paragoni.space.conf
# Edit paragoni.space.conf with your domain settings

# Build and start the containers
docker-compose up -d --build

# Initialize the database
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata movies/fixtures/initial_movies.json
docker-compose exec web python manage.py createsuperuser
```

## Development

### Running Tests

1. Run all tests:
```bash
./run_tests.sh
```

2. Run tests with coverage:
```bash
coverage run manage.py test
coverage report
coverage report -m  # for line-by-line coverage
```

3. Run specific test modules:
```bash
python manage.py test movies.tests.test_views
python manage.py test users.tests.test_views
python manage.py test reviews.tests.test_views
```

### Database Management

1. Create migrations:
```bash
python manage.py makemigrations
```

2. Apply migrations:
```bash
python manage.py migrate
```

3. Load initial data:
```bash
python manage.py loaddata movies/fixtures/initial_movies.json
```

## API Documentation

### Main Endpoints

- Movies:
  - GET `/api/movies/` - List all movies
  - GET `/api/movies/<id>/` - Movie details
  - GET `/api/movies/directors/` - List directors
  - GET `/api/movies/movements/` - List movements

- Users:
  - POST `/api/users/register/` - Register new user
  - POST `/api/users/login/` - User login
  - GET `/api/users/profile/` - User profile
  - PUT `/api/users/profile/` - Update profile
  - GET `/api/users/favorites/` - User's favorite movies

- Reviews:
  - GET `/api/reviews/` - List all reviews
  - POST `/api/reviews/` - Create review
  - GET `/api/reviews/<id>/` - Review details
  - PUT `/api/reviews/<id>/` - Update review
  - DELETE `/api/reviews/<id>/` - Delete review

## Deployment

1. Server Requirements:
   - Ubuntu 20.04 or later
   - Docker and Docker Compose installed
   - Domain name configured with DNS
   - SSL certificate (Let's Encrypt recommended)

2. Production Deployment Steps:
```bash
# Set up environment
cp .env.sample .env
# Edit .env with production values

# Configure Nginx
cp paragoni.space.conf.sample paragoni.space.conf
# Edit paragoni.space.conf with your domain

# Deploy
docker-compose -f docker-compose.yml up -d
```

## Monitoring

Access monitoring tools:
- Prometheus: `http://localhost:9093/metrics`
- Grafana: `http://localhost:3000`
  - Default dashboards for:
    - Application metrics
    - Database performance
    - System resources

## Security Features

- CSRF protection
- Secure cookie handling
- Password hashing with PBKDF2
- Rate limiting on API endpoints
- SSL/TLS encryption
- Secure headers configuration
- Environment-based security settings

## Project Structure

```
movie_rating_platform/
├── config/             # Project configuration
├── movies/            # Movie app
├── users/             # User management app
├── reviews/           # Reviews and ratings app
├── templates/         # HTML templates
├── static/            # Static files
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Run tests to ensure everything works
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Django and Django REST Framework
- UI components from Bootstrap 5
- Monitoring stack: Prometheus & Grafana
- Testing framework: Django Test Framework with Coverage.py