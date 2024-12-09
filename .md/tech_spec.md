tech_spec.md

MVC architechture:
- Models represent such entities as movies, reviews, users. 
- Views process user requests and output the result as HTML or JSON. APIs based on the Django Rest Framework have been implemented to interact with external services and mobile clients. 
- Controllers include the business logic of the application. Represented by Django View functions and ViewSet classes for working with the API.

Frontend: Django Templates + Bootstrap
Backend: Django
Database: PosgreSQL
API: Django Rest Framework

The project should be developed using the Django framework and meet the following TECHNICAL REQUIREMENTS:

1. Portability. The project should be easy to deploy, starting with cloning the repository and setting up the .env file. Database migrations should be easy to perform, with both apply and rollback support. The deployment process should be fully documented in README.md, including steps for setting up the environment.
2. Docker and containerization. All project components (including Nginx, databases, job queue) should be containerized and managed via Docker. Docker Compose is recommended for running multiple containers simultaneously.
3. CI/CD. The project should have automated testing and deployment via CI/CD, for example, using GitHub Actions or GitLab CI. Each code change should trigger an automatic test check and check the functionality of the application.
4. Django Admin. The admin panel for managing content (movies, users, reviews) should be implemented using standard Django Admin tools, with the possibility of further expansion.
5. Database. PostgreSQL is used. All database settings and migrations should be described in the documentation. Migrations should be correct and support both consistent application and rollback, which helps to avoid problems when updating the database.
6. Data fixtures. It is necessary to create fixtures containing test data (movies, reviews, users) that can be used to demonstrate and test the functionality without additional settings. If this task is difficult, it is allowed to populate the database in any available way, including raw queries in SQL, importing tables, fixtures, or manually adding data through Django Admin.

Launching the project:
1. git clone to clone the repository;
2. setting up the .env file;
3. running database migration commands: python manage.py migrate;
4. starting the server: python manage.py runserver 0.0.0.0:8000.


WEBSITE STRUCTURE

1. Main page
    1. Top popular movies (by number of ratings and reviews).
    2. Ability to filter by genre, rating and release date.
2. Catalog
    1. List of movies with the ability to filter by genre, rating, release date, authors and other parameters.
    2. Each entry in the catalog contains: title, image, short description, average rating and number of reviews.
3. Detailed movie page
    1. Full description of content, rating, block with reviews.
    2. Ability for registered users to leave a review and rate.
    3. Buttons for adding to favorites or creating custom lists.
4. Personal account
    1. User profile page where they can edit information and manage their movie lists.
    2. History of reviews and ratings left.
5. Administrative panel
    1. Manage users, movies, reviews through the standard Django admin panel.
    2. Ability to add and edit content.


FUNCTIONALITY

1. Authentication: users can register on the platform and log in to leave reviews and ratings.
2. Ratings and reviews: registered users can rate movies and and leave text reviews.
3. Filtering and sorting
    1. Users can filter movies by genre, rating, release date, authors and other characteristics.
    2. You can sort by popularity, newness, number of reviews.
4. Search: search by movie title and with case-insensitive processing.


USER ROLES AND RIGHTS ON THE WEBSITE

1. user with role ‘Administrator’ has rights:
    1. Full access to all aspects of the system through the admin panel.
    2. Content management: adding, editing and deleting movies, users, reviews.
    3. Management of categories and genres.
    4. Moderation of reviews and comments: the ability to delete or edit them.
    5. User management: activation, deactivation, assignment of roles, blocking accounts.
    6. Access to site analytics: number of views, reviews, ratings.
2. user with role ‘Moderator’ (new role) has rights:
    1. Has access to moderating reviews, comments and users, but cannot add or edit content (movies).
    2. Can block or activate users, and delete reviews that violate community rules.
    3. Moderator does not have access to database management and administrative settings.
3. user with role ‘Registered user’ has rights:
    1. Can leave reviews and ratings for films, add them to favorites or to their own lists.
    2. Can participate in discussions and leave comments.
    3. Has access to their personal account, where they can edit personal information and manage the history of reviews and ratings.
    4. Can create and manage their own lists of films (for example, "favorites", "want to watch").
4. user with role ‘Unregistered user’ has rights:
    1. Can view the catalog of films and , read reviews and use the site search.
    2. Cannot leave reviews, participate in discussions or create lists.
    3. Can register on the site to get full access to the functionality.


PAGES CONTENT
1. Site header
    1. Consists of a logo (site name), links to social networks, buttons for registration and authorization if the user is not authorized.
    2. For authorized users, a profile menu with access to a personal account and settings is displayed.
    3. The header also contains a search bar that redirects to the catalog page with results filtered by the entered query, for example, by movie title.
    4. The navigation menu contains links to the main sections of the site: home page, movie catalog, ratings, favorites.
    5. If the user is authorized, the links to registration and authorization are replaced by a profile icon and a link to the personal account.
2. Category Menu
    1. Contains movie categories for easy navigation.
    2. All active categories are displayed with a text title and an icon, if installed.
    3. The category nesting level is limited to two levels to ensure easy navigation.
3. Footer
    1. Consists of the site name, links to static pages (contacts, information about the site, rules of use).
    2. It may also contain additional links to social networks and copyright information.
4. Home (main) Page. The home page displays the following elements:
    1. Featured Content Categories: Three categories of movies selected by the administrator to be displayed on the home page. These categories can be based on popularity, new releases, or ratings.
    2. Top Content Catalog: A section with the most popular movies. This section contains the first eight movies, sorted by the number of reviews or ratings. If several objects have the same rating, the content is sorted by release date or number of views.
    3. Featured Content Slider: A section with up to 16 movies that the administrator has marked as "Featured". This content can be presented as a slider with short descriptions and ratings.
5. Catalog. The site displays a catalog of films with the ability to filter, sort and navigate by page.
    1. List of films. Each position in the catalog includes:
        1. Title.
        2. Image.
        3. Brief description.
        4. Rating (average user rating).
        5. Number of reviews.
        6. Button for adding to favorites or a custom list.
The title, image and brief description are links to the detailed page of the film. The number of reviews is also a link leading directly to the reviews section on the detailed page.
    2. Sorting. Above the catalog is a sorting block with the ability to organize content by the following parameters:
        1. By popularity (number of ratings or views).
        2. By release date (newness).
        3. By number of reviews.
        4. By average rating.
Each parameter can be sorted in ascending or descending order, but only one type of sorting can be applied at a time.
    3. Filtering. Next to the catalog is a filter that allows users to limit the content displayed by the following criteria:
        1. By title (search by part of the title, case-insensitive).
        2. By genre and category (using drop-down lists for single or multiple selection).
        3. By rating, release date and other parameters.
    4. Detailed page. The detailed page of a movie displays full information about the content, including:
        1. Detailed description.
        2. User reviews with the ability to upload additional reviews.
        3. Rating block, where authorized users can add a review and rate the content.
If the user is not authorized, when trying to leave a review or rating, a message is displayed asking them to log in.
    5. Interaction interface. Users can add movies to favorites or their lists using the button on the page.
6. Administrative Section. The admin section is only available to users with administrator rights. It is implemented using the standard Django admin panel, which provides the necessary tools for managing site data and can be easily extended.
    1. Data Management. The following subsections are available in the admin section, where the administrator can manage all aspects of the content:
        1. Users: account management, profile editing, user activation and deactivation.
        2. Movies: adding, editing, deleting content.
        3. Categories: managing movie categories.
        4. Reviews: viewing, moderating and deleting user reviews.
    2. List of Elements. Each subsection page displays a table with elements, which displays key fields for easy viewing. The administrator can:
        1. Add new elements via the corresponding button.
        2. Edit and delete existing elements via the links next to each element.
    3. Soft Delete. Data (movies, users, categories) is deleted using the soft delete mechanism. This means that deleted elements do not disappear from the database completely, but remain marked as deleted. Thanks to this, they can be restored later if necessary.
    4. Adding elements. To add new elements, the administrator uses a special form where all the necessary data can be entered. The fields are validated, and if errors occur, the user is shown the corresponding messages, and the entered data is saved for further correction.
    5. Changing elements. When editing an element, the administrator is taken to the editing page, where he can update any fields. If the data is entered incorrectly, the system will display error messages indicating the fields that require correction. After successful editing, a notification about the successful update of the element is displayed.
    6. Deleting elements. When deleting an element, the system asks for confirmation of the action. After successful deletion, a message is displayed, and when the page is reloaded, it disappears. If an error occurs during deletion, the user is shown an error message. The administrative section provides full control over the site data and provides convenient tools for managing all aspects of the project.
7. Interface and accessibility
    1. Adaptability: the application interface should be fully adaptive and support convenient display on all devices (mobile phones, tablets, computers). For styling, use Bootstrap or similar CSS frameworks that facilitate the creation of adaptive design.
    2. Intuitive navigation: navigation elements (menus, filters, search) should be easy to use, with a clear structure and logical arrangement. It is important that the user can easily find the necessary sections and content without encountering unnecessary complexity of the interface.
8. Migrations, Fixtures, and Test Data
    1. Database Migrations. All changes to the database structure must be correctly documented via Django migrations. Migrations must be consistent and rollback-safe. It is important to ensure that migrations work the same way both locally and on the server (in a Docker container or in production).
    2. Fixtures. Create fixtures containing test data that includes sample movies, users, reviews, and ratings. These fixtures will help developers and testers quickly deploy the project with minimal effort and will provide the ability to demonstrate the project without additional configuration.
    3. Uploaded Data. Make sure that all data in the fixtures corresponds to real-world usage of the platform. This means that the database should have test movies of different genres, ratings, reviews, and multiple user levels with different permissions (e.g. admin, regular user, moderator).
    4. Automatic application of fixtures. Include instructions in README.md that describe how to automatically load fixtures after running database migrations. For example, python manage.py loaddata <fixture name> should be part of the deployment process.
    5. Dynamic test data. Consider generating dynamic test data using libraries like Faker to create a large, varied set of data that can be used for load and performance testing.
    6. Test cases. Include test cases that verify that the data is loaded correctly and interacts with the core components of the application. This ensures that migrations and fixtures not only load correctly, but also work in conjunction with other parts of the system.
