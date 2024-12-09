Project_Evaluation_Criteria.md (let’s keep in mind the below as well as the tech_spec.md, so that we make sure to align all our work with the criteria):

These criterias will help evaluate the project in terms of its functionality, code quality, user friendliness, security, and performance. By fulfilling all of the criteria, we should be able to successfully implement a scalable, secure, and user-friendly online movie rating platform.

1. Functionality. The application must correctly implement all of the specified requirements, including:
    1. Ability to register and authenticate users.
    2. View, add, and delete movie reviews and ratings.
    3. Filter and sort content by various parameters (genres, release date, rating).
    4. Manage user access levels (administrators, moderators, authorized and unauthorized users).
    5. Use Django Admin to manage data (movies, reviews).
    6. The platform must support scalability, for example, adding new features such as recommendations or automatically updating data via API.
2. Code quality:
    1. The code must be written in accordance with PEP8 standards.
    2. Using modern development practices in Django:
        1. Using Class-Based Views (CBV) and Generic Views where appropriate.
        2. Separation of logic between models, views, and templates (MVC).
        3. Clean and readable code, including the use of comments and documentation.
    3. Minimizing repetitive code and proper project structure (for example, using Django applications to separate logic).
    4. Handling errors and exceptions.
3. User interface
    1. A pleasant and intuitive interface implemented using Django Templates, HTML, CSS, and Bootstrap.
    2. Consistent page styling, easy site navigation.
    3. Support for responsive design for correct display on various devices (mobile, tablet, desktop).
    4. Implementation of convenient forms for adding reviews, feedback, and interacting with content.
4. Containerization. The application must be fully containerized using Docker:
    1. Dockerfile for the web application and database (PostgreSQL).
    2. Using Docker Compose to manage multiple containers (e.g. Django, PostgreSQL, Nginx).
    3. Correct operation of services in containers, including interaction between the web application, database, and Nginx.
    4. Logically configured network and mounting of directories for exchanging data between containers.
5. CI/CD. Automated process of building, testing, and deploying the application using GitHub Actions, GitLab CI, or a similar tool is configured:
    1. Automatically running tests with each commit and pull request.
    2. Automation of application deployment on the server (staging or production).
    3. Notifications about CI/CD results in GitHub or another version control system.
6. Security. Security measures have been implemented:
    1. Correct configuration of access rights to data (e.g. separation of rights between administrators, moderators, and users).
    2. Protection against attacks such as XSS, SQL injections, and CSRF.
    3. Manage sensitive data via .env files or Docker Secrets.
7. Monitoring and logging. Monitoring and logging mechanisms are configured:
    1. Logging of all key application events, including errors and information messages.
    2. Ability to track the state of the application via logs and metrics.
8. Testing
    1. Availability of tests with sufficient coverage:
        1. Unit tests to check the main components of the system (e.g. working with the movie model, user registration, adding reviews).
        2. Integration tests to check the interaction between components.
    2. Automatically run tests with each change in the project as part of CI/CD.
