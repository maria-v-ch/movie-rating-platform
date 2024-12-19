from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from movies.models import Movie
from movies.views import IsAdminOrReadOnly
from reviews.models import Rating, Review

User = get_user_model()


class MovieViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass123"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
            slug="test-movie",
        )
        self.movie2 = Movie.objects.create(
            title="Another Movie",
            director="Another Director",
            release_year=2019,
            description="Another Description",
            runtime=110,
            country="Another Country",
            movement="Test Movement",
            slug="another-movie",
        )
        self.review = Review.objects.create(user=self.user, movie=self.movie, text="Great movie!")
        self.rating = Rating.objects.create(user=self.user, movie=self.movie, score=Decimal("4.5"))

    def test_movie_list_view(self):
        """Test the movie list view"""
        response = self.client.get(reverse("movies:movie-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_list.html")
        self.assertContains(response, "Test Movie")
        self.assertContains(response, "Another Movie")

    def test_movie_list_view_with_filters(self):
        """Test movie list view with filters"""
        # Test director filter
        response = self.client.get(reverse("movies:movie-list") + "?director=Test Director")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Movie")
        self.assertNotContains(response, "Another Movie")

        # Test movement filter
        response = self.client.get(reverse("movies:movie-list") + "?movement=Test Movement")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Movie")
        self.assertContains(response, "Another Movie")

        # Test year filter
        response = self.client.get(reverse("movies:movie-list") + "?year=2020")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Movie")
        self.assertNotContains(response, "Another Movie")

    def test_movie_list_context_data(self):
        """Test movie list view context data"""
        response = self.client.get(reverse("movies:movie-list"))
        self.assertEqual(response.status_code, 200)

        # Check directors in context
        directors = response.context["directors"]
        self.assertEqual(len(directors), 2)
        director_names = [d["director"] for d in directors]
        self.assertIn("Test Director", director_names)
        self.assertIn("Another Director", director_names)

        # Check movements in context
        movements = response.context["movements"]
        self.assertEqual(len(movements), 1)
        movement_names = [m["movement"] for m in movements]
        self.assertIn("Test Movement", movement_names)

        # Check years in context
        years = response.context["years"]
        self.assertEqual(len(years), 2)
        self.assertIn(2020, years)
        self.assertIn(2019, years)

    def test_movie_detail_view(self):
        """Test the movie detail view"""
        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": self.movie.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_detail.html")
        self.assertContains(response, "Test Movie")
        self.assertContains(response, "Test Director")
        self.assertContains(response, "Great movie!")  # Review text
        self.assertContains(response, "4.5")  # Rating score

    def test_movie_detail_view_context_data(self):
        """Test movie detail view context data"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": self.movie.slug}))
        self.assertEqual(response.status_code, 200)

        # Check reviews and user ratings in context
        reviews = response.context["reviews"]
        user_ratings = response.context["user_ratings"]
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].text, "Great movie!")
        self.assertEqual(user_ratings[self.user.id].score, Decimal("4.5"))

        # Check user review and rating in context
        self.assertEqual(response.context["user_review"], self.review)
        self.assertEqual(response.context["user_rating"], self.rating)

        # Check similar movies (should only include movie2 since it's the only other movie)
        similar_movies = response.context["similar_movies"]
        self.assertEqual(len(similar_movies), 1)
        self.assertEqual(similar_movies[0], self.movie2)

    def test_director_list_view(self):
        """Test the director list view"""
        response = self.client.get(reverse("movies:directors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/director_list.html")

        directors = response.context["directors"]
        self.assertEqual(len(directors), 2)

        # Check director stats
        for director in directors:
            if director["director"] == "Test Director":
                self.assertEqual(director["movie_count"], 1)
                self.assertEqual(director["rated_count"], 1)
                self.assertEqual(director["avg_rating"], Decimal("4.5"))
            else:
                self.assertEqual(director["movie_count"], 1)
                self.assertEqual(director["rated_count"], 0)
                self.assertIsNone(director["avg_rating"])

    def test_movement_list_view(self):
        """Test the movement list view"""
        response = self.client.get(reverse("movies:movements"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movement_list.html")

        movements = response.context["movements"]
        self.assertEqual(len(movements), 1)

        # Check movement stats
        for movement in movements:
            if movement["movement"] == "Test Movement":
                self.assertEqual(movement["movie_count"], 2)
                self.assertEqual(movement["rated_count"], 1)
                self.assertEqual(movement["avg_rating"], Decimal("4.5"))

    def test_movie_list_pagination(self):
        """Test movie list pagination"""
        # Create 15 more movies (total 17)
        for i in range(15):
            Movie.objects.create(
                title=f"Movie {i}",
                director="Test Director",
                release_year=2020,
                description=f"Description {i}",
                runtime=120,
                country="Test Country",
                movement="Test Movement",
                slug=f"movie-{i}",
            )

        # Test first page
        response = self.client.get(reverse("movies:movie-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 12)  # paginate_by = 12

        # Test second page
        response = self.client.get(reverse("movies:movie-list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 5)  # remaining movies

    def test_movie_list_invalid_page(self):
        """Test movie list view with invalid page number"""
        # Create enough movies for pagination (paginate_by = 12)
        for i in range(15):
            Movie.objects.create(
                title=f"Movie {i}",
                director="Test Director",
                release_year=2020,
                description=f"Description {i}",
                runtime=120,
                country="Test Country",
                movement="Test Movement",
                slug=f"movie-{i}",
            )

        # Test with page number that's too high
        response = self.client.get(reverse("movies:movie-list") + "?page=999")
        self.assertEqual(response.status_code, 404)

        # Test with non-numeric page
        response = self.client.get(reverse("movies:movie-list") + "?page=abc")
        self.assertEqual(response.status_code, 404)

        # Test with negative page
        response = self.client.get(reverse("movies:movie-list") + "?page=-1")
        self.assertEqual(response.status_code, 404)

        # Test with valid first page
        response = self.client.get(reverse("movies:movie-list") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["movies"]), 12)  # First page shows 12 movies

    def test_movie_list_empty_filters(self):
        """Test movie list view with empty filter values"""
        response = self.client.get(reverse("movies:movie-list") + "?director=&movement=&year=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 2)
        self.assertEqual(response.context["current_director"], "")
        self.assertEqual(response.context["current_movement"], "")
        self.assertEqual(response.context["current_year"], "")

    def test_movie_detail_unauthenticated(self):
        """Test movie detail view when user is not authenticated"""
        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": self.movie.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_detail.html")
        self.assertNotIn("user_review", response.context)
        self.assertNotIn("user_rating", response.context)

    def test_movie_detail_no_reviews(self):
        """Test movie detail view for movie with no reviews"""
        movie3 = Movie.objects.create(
            title="No Reviews Movie",
            director="Test Director",
            release_year=2021,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
            slug="no-reviews-movie",
        )
        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": movie3.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["reviews"]), 0)
        self.assertEqual(len(response.context["user_ratings"]), 0)

    def test_empty_director_list(self):
        """Test director list view with empty database"""
        Movie.objects.all().delete()
        response = self.client.get(reverse("movies:directors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/director_list.html")
        self.assertEqual(len(response.context["directors"]), 0)

    def test_empty_movement_list(self):
        """Test movement list view with empty database"""
        Movie.objects.all().delete()
        response = self.client.get(reverse("movies:movements"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movement_list.html")
        self.assertEqual(len(response.context["movements"]), 0)

    def test_movie_detail_with_similar_movies(self):
        """Test movie detail view's similar movies feature"""
        # Create a movie with same director but different movement
        movie3 = Movie.objects.create(
            title="Same Director Movie",
            director="Test Director",
            release_year=2021,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Different Movement",
            slug="same-director-movie",
        )

        # Create a movie with same movement but different director
        movie4 = Movie.objects.create(
            title="Same Movement Movie",
            director="Different Director",
            release_year=2021,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
            slug="same-movement-movie",
        )

        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": self.movie.slug}))
        self.assertEqual(response.status_code, 200)
        similar_movies = response.context["similar_movies"]
        self.assertEqual(len(similar_movies), 3)  # movie2, movie3, and movie4 are similar
        self.assertIn(movie3, similar_movies)  # Same director
        self.assertIn(movie4, similar_movies)  # Same movement

    def test_movie_detail_authenticated(self):
        """Test movie detail view when user is authenticated"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": self.movie.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_detail.html")
        self.assertEqual(response.context["user_review"], self.review)
        self.assertEqual(response.context["user_rating"], self.rating)

        # Test with a movie the user hasn't reviewed or rated
        movie3 = Movie.objects.create(
            title="No User Review Movie",
            director="Test Director",
            release_year=2021,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
            slug="no-user-review-movie",
        )
        response = self.client.get(reverse("movies:movie-detail", kwargs={"slug": movie3.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["user_review"])
        self.assertIsNone(response.context["user_rating"])


class IsAdminOrReadOnlyTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass123"
        )
        self.permission = IsAdminOrReadOnly()

    def test_safe_methods(self):
        """Test permission for safe methods (GET, HEAD, OPTIONS)"""
        request = Request(self.factory.get("/api/v1/movies/"))
        request.user = AnonymousUser()
        self.assertTrue(self.permission.has_permission(request, None))

        request = Request(self.factory.head("/api/v1/movies/"))
        request.user = AnonymousUser()
        self.assertTrue(self.permission.has_permission(request, None))

        request = Request(self.factory.options("/api/v1/movies/"))
        request.user = AnonymousUser()
        self.assertTrue(self.permission.has_permission(request, None))

    def test_unsafe_methods(self):
        """Test permission for unsafe methods (POST, PUT, DELETE)"""
        # Test unauthenticated user
        request = Request(self.factory.post("/api/v1/movies/"))
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))

        # Test regular user
        request = Request(self.factory.post("/api/v1/movies/"))
        request.user = self.user
        self.assertFalse(self.permission.has_permission(request, None))

        # Test admin user
        request = Request(self.factory.post("/api/v1/movies/"))
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, None))


class MovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass123"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
            slug="test-movie",
        )

    def test_permission_class(self):
        """Test IsAdminOrReadOnly permission class"""
        permission = IsAdminOrReadOnly()

        # Test GET request (safe method)
        request = self.factory.get("/api/v1/movies/")
        request.user = AnonymousUser()
        self.assertTrue(permission.has_permission(request, None))

        # Test POST request with anonymous user
        request = self.factory.post("/api/v1/movies/")
        request.user = AnonymousUser()
        self.assertFalse(permission.has_permission(request, None))

        # Test POST request with regular user
        request = self.factory.post("/api/v1/movies/")
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))

        # Test POST request with admin user
        request = self.factory.post("/api/v1/movies/")
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))

    def test_movie_filter(self):
        """Test MovieFilter functionality"""
        # Create additional movies for filtering
        Movie.objects.create(
            title="Movie 2020",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="New Wave",
            slug="movie-2020",
        )
        Movie.objects.create(
            title="Movie 2021",
            director="Other Director",
            release_year=2021,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
            slug="movie-2021",
        )

        # Test year filter
        response = self.client.get("/api/v1/movies/", {"release_year": 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Test movement filter
        response = self.client.get("/api/v1/movies/", {"movement": "New Wave"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Test director filter
        response = self.client.get("/api/v1/movies/", {"director": "Other Director"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Test combined filters
        response = self.client.get("/api/v1/movies/", {"release_year": 2020, "director": "Test Director"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_movie_viewset_create(self):
        """Test MovieViewSet create functionality"""
        self.client.force_authenticate(user=self.admin_user)

        # Test creating movie with special characters
        data = {
            "title": 'Test Movie & Special "Characters"',
            "director": "Test Director",
            "release_year": 2020,
            "description": 'Description with & and "quotes"',
            "runtime": 120,
            "country": "Test Country",
            "movement": "Test Movement",
            "slug": "test-movie-2",
            "poster": None,
            "backdrop": None,
        }
        response = self.client.post("/api/v1/movies/", data, format="json")
        print("Create response:", response.status_code)  # Debug
        print("Create response data:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify special characters were escaped
        movie = Movie.objects.get(slug=response.data["slug"])  # Use slug from response
        self.assertEqual(movie.title, "Test Movie &amp; Special &quot;Characters&quot;")
        self.assertEqual(movie.description, "Description with &amp; and &quot;quotes&quot;")

    def test_movie_viewset_update(self):
        """Test MovieViewSet update functionality"""
        self.client.force_authenticate(user=self.admin_user)

        # Test updating movie with special characters
        data = {
            "title": 'Updated Movie & Special "Characters"',
            "description": 'Updated Description with & and "quotes"',
            "director": "Test Director",
            "release_year": 2020,
            "runtime": 120,
            "country": "Test Country",
            "movement": "Test Movement",
        }
        response = self.client.patch(f"/api/v1/movies/{self.movie.slug}/", data, format="json")
        print("Update response:", response.status_code)  # Debug
        print("Update response data:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify special characters were escaped
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, "Updated Movie &amp; Special &quot;Characters&quot;")
        self.assertEqual(self.movie.description, "Updated Description with &amp; and &quot;quotes&quot;")

    def test_movie_favorite_action(self):
        """Test MovieViewSet favorite action"""
        # Test unauthenticated
        response = self.client.post(f"/api/v1/movies/{self.movie.slug}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test favoriting
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/v1/movies/{self.movie.slug}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "favorited")
        self.assertTrue(self.movie.favorited_by.filter(id=self.user.id).exists())

        # Test unfavoriting
        response = self.client.post(f"/api/v1/movies/{self.movie.slug}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "unfavorited")
        self.assertFalse(self.movie.favorited_by.filter(id=self.user.id).exists())
