# Movie Rating Platform 🎬

A Django-based platform for rating and reviewing art-house films, similar to IMDb but focused on art cinema. The platform allows users to browse movies, leave reviews, and rate films while providing detailed information about art-house movements and cinematography.

## ✨ Features

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
- Advanced container health monitoring
- Robust database connection management

## 🛠 Tech Stack

- Python 3.12
- Django 5.0
- Django REST Framework
- PostgreSQL 15
- Docker & Docker Compose
- Nginx with advanced DNS resolution
- Prometheus & Grafana
- GitHub Actions for CI/CD
- Bootstrap 5 for frontend

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- Python 3.12+ (for local development)
- virtualenv (optional, for local development)

## 🚀 Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/maria-v-ch/movie-rating-platform.git
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
```

### B. Production Setup
```bash
# Copy production environment file
cp .env.sample .env

# Edit .env with your production settings
# Make sure to set strong passwords and proper domain settings

# Build and start the containers
docker-compose up -d --build

# Initialize the database
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata movies/fixtures/initial_movies.json
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Development

### Running Tests
```bash
# Run all tests
./run_tests.sh

# Run tests with coverage
coverage run manage.py test
coverage report
coverage report -m  # for line-by-line coverage

# Run specific test modules
python manage.py test movies.tests.test_views
```

## 📡 API Documentation

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

## 🗄️ Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load initial data
python manage.py loaddata movies/fixtures/initial_movies.json
```

## 🚀 Deployment

### Server Requirements
- Ubuntu 20.04 or later
- Docker and Docker Compose installed
- Domain name configured with DNS
- SSL certificate (Let's Encrypt recommended)

### Production Deployment Features
- Advanced container health monitoring
- Robust database connection management
- Nginx with Docker DNS resolution
- Automated SSL certificate management
- Zero-downtime deployments

### Deployment Steps
```bash
# Set up environment
cp .env.sample .env
# Edit .env with production values

# Deploy
docker-compose -f docker-compose.yml up -d
```

## 📊 Monitoring

Access monitoring tools:
- Prometheus: `http://localhost:9093/metrics`
- Grafana: `http://localhost:3000`
  - Real-time application metrics
  - Database performance monitoring
  - System resource tracking
  - Custom health check dashboards

## 👨‍💼 Admin Interface

The admin interface is available at `/admin/`. Use it to:
- Manage users and permissions
- Moderate reviews and content
- Monitor site activity
- Manage movie database

Default admin credentials are managed through environment variables:
```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword
```

## 🔒 Security Features

- CSRF protection
- Secure cookie handling
- Password hashing with PBKDF2
- Rate limiting on API endpoints
- SSL/TLS encryption
- Secure headers configuration
- Environment-based security settings
- Advanced database connection security

## 📁 Project Structure
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

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests
4. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with Django and Django REST Framework
- UI components from Bootstrap 5
- Monitoring: Prometheus & Grafana
- Testing: Django Test Framework with Coverage.py
