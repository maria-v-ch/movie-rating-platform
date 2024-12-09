stage1.md

Infrastructure Preparation and Database Design.

Database Architecture Design
1. Design the database architecture for storing information about movies, reviews, users.
2. Define relationships between entities (e.g. OneToMany for reviews and movies, ManyToMany for users' favorites lists).
3. Draw a database diagram including the main entities and their relationships (or let’s visualize it in any possible way if any,just in case. Though I believe it’s not that nessesary cinse our project is not that big):
    1. Tables: movies, reviews, ratings, users.
    2. Relationships: one movie can have many reviews (OneToMany relationship), users can rate movies (ManyToMany relationship).
4. Prepare technical documentation for the database, describing the main entities, their attributes and relationships.

Database Development (Storage)
The main project database is implemented using PostgreSQL, providing a reliable and scalable data storage for all platform entities (movies, and, users, reviews, ratings).

Database Design Steps
1. Developing a database architecture for storing information about movies, reviews, users.
2. Models. Each entity (movies, reviews, users) is represented as a Django model. Models define fields and relationships between entities.
3. Relationships:
    1. OneToMany — one movie can have many reviews and ratings.
    2. ManyToMany — users can add movies to favorites.
4. Indexes. To improve database performance, we recommend using indexes on fields that are often used in filtering and sorting (e.g. rating, release date).
5. Data Normalization. The database is normalized to avoid data redundancy and provide flexibility of the structure when scaling the system.
6. Drawing a database schema including the main entities and their relationships:
    1. Tables: movies, reviews, ratings, users.
    2. Relationships: one movie can have many reviews (OneToMany relationship), users can rate movies (ManyToMany relationship).
7. Preparing technical documentation for the database with a description of the main entities, their attributes and relationships.
8. Migrations. The entire database structure is created and modified through the Django migration system. Migrations must be correctly configured for consistent application and rollback of changes.
9. Backup and recovery. We recommend implementing a mechanism for creating database backups and restoring data in the event of a failure. If this task is difficult, you can fill the database in any available way, including raw queries in SQL, importing tables, fixtures or manually adding data through Django Admin.
10. Data fixtures. Data fixtures are provided to demonstrate the functionality and test the system. These fixtures contain test data such as sample movies, , reviews, users.

Preparing the project infrastructure
1. Set up the development environment. Prepare and configure the following tools:
    1. Docker for project containerization (create a Dockerfile for the project environment).
    2. PostgreSQL for data storage (set up a database via Docker).
    3. Docker Compose for managing services (e.g. a database, a future server).
    4. Git for version control (create a repository for the project on GitHub or GitLab).
2. Ensure preparation for automatic deployment of the project on the server using Docker and Docker Compose.

Set up the environment for the database:
1. Install and configure PostgreSQL to work with the future Django application.
2. Prepare basic commands for managing database migrations via Docker (e.g. commands for creating and restoring backups).
Stage results

As a result of working on this stage, you should have a fully prepared infrastructure for working with the project (Docker, database, git repository) and a ready technical description of the database with a drawn diagram (in any program, for example dbdesigner.net) with the described connections - we can use our internal capabilities for this.