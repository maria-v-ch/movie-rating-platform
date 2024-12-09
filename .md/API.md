API.md

Writing an API Using Django Rest Framework (DRF)

Within the project we develop an API for a movie rating platform using Django Rest Framework (DRF). The API will provide access to movie, review, and rating data, and will allow interaction with the system through a front-end (e.g. a mobile app or external services).

Tasks

1. Setting up Django Rest Framework
    1. Connect and configure DRF in the project.
    2. Add the necessary settings insettings.py for API operation, including authentication, pagination and response formatting settings.
2. Creating Serializers
    1. Create serializers for the Movies, Reviews, and Ratings models.
    2. Provide support for reading (GET requests) and creating/editing data (POST/PUT/DELETE).
3. API for reviews and ratings
    1. Implement endpoints for working with movies:
        1. Getting a list of movies (with support for filtering by genre, rating, release date and other parameters).
        2. Obtaining detailed information about the film.
        3. Adding, updating and deleting movie data (available only to administrator).
4. Authentication and Authorization
    1. Implement authentication via JWT (JSON Web Tokens) or standard DRF authentication.
    2. Ensure endpoint protection: only authorized users can leave reviews and ratings, administrators can manage content (movies).
5. Pagination and filtering
    1. Set up pagination for movie list and reviews.
    2. Add filtering and sorting by key parameters (for example, by genre, rating, date).
6. API Documentation
    1. Add documentation for the API using drf-yasg or Django REST Swagger . This will allow developers and API users to see the structure of available endpoints and example requests.
7. API Testing
    1. Write tests for all key API endpoints usingpytestor built-in DRF testing tools.
    2. Make sure that tests cover all CRUD operations and check the availability of endpoints for different types of users (unregistered, registered, administrator).

Example of endpoints:
* GET /api/movies/— getting a list of films (with filtering and sorting).
* GET /api/movies/{id}/- obtaining detailed information about a specific film.
* POST /api/movies/- adding a new movie (administrators only).
* PUT /api/movies/{id}/- editing information about the film (administrators only).
* DELETE /api/movies/{id}/- deleting a movie (administrators only).
* GET /api/reviews/{movie_id}/- getting reviews for a specific film.
* POST /api/reviews/— adding a review and rating (authorized users only).

Additional options
* Implement caching support for frequently accessed data (e.g. popular movies) using Django Cache Framework or Redis.
* Support international users through multilingual API responses (e.g. using libraries to translate data).

This task is aimed at implementing an API interface for interacting with the system through external applications. This will help not only expand the functionality of the platform, but also strengthen skills in working with the Django Rest Framework, as well as authentication and API documentation.



