from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.html import escape
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie

User = get_user_model()


class MovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.movie_data = {
            "title": "New Movie",
            "director": "New Director",
            "release_year": 2021,
            "description": "New Description",
            "runtime": 130,
            "country": "New Country",
            "movement": "New Movement",
            "slug": "new-movie",
            "poster_url": "https://example.com/poster.jpg",
        }

    def test_list_movies(self):
        """Test listing movies"""
        response = self.client.get("/api/v1/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Movie")

    def test_create_movie_unauthorized(self):
        """Test creating a movie without admin privileges"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/movies/", self.movie_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_admin(self):
        """Test creating a movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/v1/movies/", self.movie_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 2)
        self.assertEqual(Movie.objects.get(slug="new-movie").title, "New Movie")

    def test_update_movie_admin(self):
        """Test updating a movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f"/api/v1/movies/{self.movie.slug}/", {"title": "Updated Movie"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, "Updated Movie")

    def test_delete_movie_admin(self):
        """Test deleting a movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/api/v1/movies/{self.movie.slug}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Movie.objects.count(), 0)

    def test_movie_filters(self):
        """Test movie filtering"""
        # Create another movie for testing filters
        Movie.objects.create(
            title="Another Movie",
            director="Another Director",
            release_year=2019,
            description="Another Description",
            runtime=110,
            country="Another Country",
            movement="Another Movement",
            slug="another-movie",
        )

        # Test year filter
        response = self.client.get("/api/v1/movies/", {"release_year": 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Movie")

        # Test movement filter
        response = self.client.get("/api/v1/movies/", {"movement": "Test Movement"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Movie")

        # Test director filter
        response = self.client.get("/api/v1/movies/", {"director": "Test Director"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Movie")

    def test_movie_search(self):
        """Test movie search"""
        response = self.client.get("/api/v1/movies/", {"search": "Test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Movie")

    def test_movie_ordering(self):
        """Test movie ordering"""
        Movie.objects.create(
            title="Another Movie",
            director="Another Director",
            release_year=2019,
            description="Another Description",
            runtime=110,
            country="Another Country",
            movement="Another Movement",
            slug="another-movie",
        )

        # Test ordering by release year ascending
        response = self.client.get("/api/v1/movies/", {"ordering": "release_year"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Another Movie")

        # Test ordering by title descending
        response = self.client.get("/api/v1/movies/", {"ordering": "-title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Test Movie")

    def test_favorite_action(self):
        """Test favoriting and unfavoriting a movie"""
        self.client.force_authenticate(user=self.user)

        # Test favoriting
        response = self.client.post(f"/api/v1/movies/{self.movie.slug}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "favorited")
        self.assertTrue(self.movie.favorited_by.filter(id=self.user.id).exists())

        # Test unfavoriting
        response = self.client.post(f"/api/v1/movies/{self.movie.slug}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "unfavorited")
        self.assertFalse(self.movie.favorited_by.filter(id=self.user.id).exists())

    def test_favorite_action_unauthenticated(self):
        """Test favoriting a movie when not authenticated"""
        response = self.client.post(f"/api/v1/movies/{self.movie.slug}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_html_escaping(self):
        """Test that HTML in movie data is properly escaped"""
        self.client.force_authenticate(user=self.admin_user)
        data = self.movie_data.copy()
        data.update(
            {
                "title": '<script>alert("XSS")</script>Title',
                "description": '<script>alert("XSS")</script>Description',
                "poster_url": "https://example.com/poster.jpg",
            }
        )
        response = self.client.post("/api/v1/movies/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        movie = Movie.objects.get(slug="new-movie")
        self.assertEqual(movie.title, escape('<script>alert("XSS")</script>Title'))
        self.assertEqual(movie.description, escape('<script>alert("XSS")</script>Description'))
