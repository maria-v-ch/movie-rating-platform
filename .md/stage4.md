stage4.md

Steps to follow at stage 4:
1. Project Completion. Perform final testing of all project components:
    1. Check the system functionality: filtering, sorting, adding reviews and comments.
    2. Check the admin panel for correct content management (movies, reviews, users).
    3. Test that the database and web application interact correctly.
2. Additional improvements.
    1. Implement any interface improvements and enhancements:
        1. Optimize data and page loading if there are display delays.
        2. Improve styling using Bootstrap for more convenient user interaction with content.
    2. Check the adaptability of the site on different devices (mobile, tablets, desktops) and make edits to improve the user experience.
3. API development (see API.md for details).
    1. Implement a REST API for interaction with the system:
        1. Use Django Rest Framework (DRF) to create an API.
        2. Create serializers and endpoints for working with movies, reviews, and ratings.
        3. Enable authentication features via JWT to ensure API security.
        4. Document the API using drf-yasg or Swagger.
4. Documentation and deployment
    1. Improve the project documentation:
        1. Describe all the steps taken, including project settings and deployment.
        2. Document the installation, launch, deployment, and testing process.
    2. Make sure the entire project deployment process is clear and easily reproducible:
        1. Configure the launch of Docker containers and check that all services are working correctly.
        2. Check that the project is successfully deployed to a server with support for all the specified functions (admin panel, frontend, database).

At this stage we complete the project taking into account all mandatory requirements:
- final testing completed
- interface finalized,
- deployment and project documentation provided.
- Development of REST API.
