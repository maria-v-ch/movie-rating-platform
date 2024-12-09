stage3.md

At this stage we will finalize the Django project, add tests and connect docker. We can use the structure described in stage3_pec.md or our own if the one in the file seems not modern or technically correct.

Stage 3 execution steps are the following:
1. Writing unit and integration tests
    1. Develop unit tests for all key components:
        1. Tests for models (movies, reviews, users) for correct operation of CRUD operations.
        2. Tests for views for correct display of pages and processing of requests.
        3. Testing the functionality of filtering and sorting content.
    2. Develop integration tests to check the interaction between components:
        1. Checking the operation of templates with models and views.
        2. Tests for interaction with the database.
    3. Write tests to check security, including:
        1. Checking the correct operation of authorization and authentication of users.
        2. Checking access rights to pages and functionality (for example, the ability to add reviews only by authorized users).
2. Setting up CI/CD.
    1. Set up an automatic process for building, testing, and deploying the application:
        1. Connect CI/CD via GitHub Actions or GitLab CI.
        2. Set up automatic launch of all tests with each commit and pull request.
        3. Make sure that each pull request is checked for errors in the code and that all tests have passed successfully.
    2. Set up automatic deployment to the server (staging or production) upon successful completion of all tests and checks.
3. Setting up Docker and containerization.
    1. Create a Dockerfile for containerization of the project:
        1. Describe the assembly of the Django application with its dependencies.
        2. Set up a PostgreSQL database in a Docker container.
    2. Set up Docker Compose to manage multiple containers:
        1. Container for the Django application.
        2. Container for the PostgreSQL database.
        3. A container for Nginx that will handle requests and statics.
    3. Make sure that all services are properly connected to each other via the Docker network.
4. Configuring Nginx and security.
    1. Configure Nginx to work as a reverse proxy:
        1. Routing requests to the Django application.
        2. Processing static files (CSS, JS).
        3. Configure security via HTTPS.
    2. Configure SSL certificates to ensure a secure connection to the project via HTTPS.
5. Deploy the application to the server.
    1. Deploy the application to the server with a fully configured environment:
        1. Launching containers via Docker Compose.
        2. Applying database migrations.
        3. Downloading and deploying fixtures for test data (movies, reviews, users).
    2. Make sure that all services are working correctly and the project is accessible via HTTPS.
6. Testing and monitoring
    1. Conduct load tests to check the system performance with a large volume of data and users.
    2. Configure a monitoring system to track the application status (for example, using Prometheus or other tools).
    3. Configure logging of all key events (errors, user requests) for further analysis.

Third Stage results are that after completing this stage, the project should be:
1. Fully tested and ready for deployment on the server.
2. Configured CI/CD to automate testing and deployment.
3. The application is containerized using Docker and ready for scaling.
4. The project is available via HTTPS through Nginx, with all services (Django application, PostgreSQL, Nginx) working correctly.
