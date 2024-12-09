# Movie Rating Platform

A Django-based platform for rating and reviewing art-house films, similar to IMDb but focused on art cinema. The platform allows users to browse movies, leave reviews, and rate films while providing detailed information about art-house movements and cinematography.

## Features

- Browse and search art-house films
- User registration and authentication
- Movie reviews and ratings
- Detailed movie information including cinematographers and art movements
- Admin interface for content management
- RESTful API with JWT authentication
- Monitoring with Prometheus and Grafana

## Tech Stack

- Python 3.9
- Django 5.1
- Django REST Framework
- PostgreSQL 13
- Docker & Docker Compose
- Nginx
- Prometheus & Grafana
- GitHub Actions for CI/CD

## Prerequisites

- Docker and Docker Compose
- Git
- Make (optional, for using Makefile commands)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd movie_rating_platform
```

2. Create environment file:
```bash
cp .env.sample .env
# Edit .env with your settings
```

3. Build and start the containers:
```bash
docker-compose up -d --build
```

4. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Load initial data:
```bash
docker-compose exec web python manage.py loaddata movies/fixtures/initial_movies.json
```

## Development

1. Run tests:
```bash
docker-compose exec web python manage.py test
```

2. Run tests with coverage:
```bash
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage report
```

3. Create migrations:
```bash
docker-compose exec web python manage.py makemigrations
```

4. Apply migrations:
```bash
docker-compose exec web python manage.py migrate
```

## API Documentation

The API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

### Main Endpoints

- `/api/v1/movies/` - Movie endpoints
- `/api/v1/users/` - User management endpoints
- `/api/v1/reviews/` - Review and rating endpoints

## Deployment

1. Set up your server with Docker and Docker Compose

2. Configure environment variables on your server:
```bash
cp .env.sample .env
# Edit .env with production settings
```

3. Set up SSL certificates:
```bash
certbot certonly --webroot -w /var/www/html -d paragoni.space -d www.paragoni.space
```

4. Deploy using Docker Compose:
```bash
docker-compose -f docker-compose.yml up -d
```

## Monitoring

- Prometheus metrics: `http://localhost:9093`
- Grafana dashboard: `http://localhost:3000`

## Testing

The project includes several types of tests:

1. Unit tests for models, views, and serializers
2. Integration tests for API endpoints
3. Security tests for authentication and authorization
4. Performance tests for database operations

Run specific test modules:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test movies.tests
python manage.py test users.tests
python manage.py test reviews.tests
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 