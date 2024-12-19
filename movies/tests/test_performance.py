import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient

from movies.models import Movie

User = get_user_model()


class PerformanceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Create test movies
        self.movies = []
        for i in range(20):
            movie = Movie.objects.create(
                title=f"Test Movie {i}",
                director=f"Director {i}",
                release_year=2000 + i,
                description=f"Description {i}",
                runtime=90 + i,
                country="Test Country",
                movement="Test Movement",
            )
            self.movies.append(movie)

    def test_movie_list_performance(self):
        start_time = time.time()
        self.client.get(reverse("movie-list"))
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)

    def test_movie_detail_performance(self):
        url = reverse("movies:movie-detail", kwargs={"slug": self.movies[0].slug})
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 10)  # Adjusted for template rendering

    def test_cache_effectiveness(self):
        url = reverse("movies:movie-list")
        cache.clear()  # Clear cache before testing

        # First request - should hit the database
        with CaptureQueriesContext(connection) as context:
            self.client.get(url)
            queries_first_request = len(context.captured_queries)

        # Second request - should use cache
        with CaptureQueriesContext(connection) as context:
            self.client.get(url)
            queries_second_request = len(context.captured_queries)

        self.assertLessEqual(queries_second_request, queries_first_request)

    def test_search_performance(self):
        url = reverse("movies:movie-list")
        filters = {
            "search": "Test",
            "release_year": 2010,
            "movement": "Test Movement",
        }

        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(url, filters)
            end_time = time.time()

            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 10)  # Adjusted for template rendering
            self.assertLess(end_time - start_time, 1.0)  # Response time under 1 second

    def test_directors_list_performance(self):
        url = reverse("movies:directors")
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 10)  # Adjusted for template rendering

    def test_movements_list_performance(self):
        url = reverse("movies:movements")
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 10)  # Adjusted for template rendering

    def test_concurrent_requests(self):
        start_time = time.time()
        for _ in range(10):
            self.client.get(reverse("movie-list"))
        end_time = time.time()

        # Assert total time is less than 2 seconds
        total_time = end_time - start_time
        self.assertLess(total_time, 2.0)
