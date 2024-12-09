from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from movies.models import Movie
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.core.cache import cache
from django.conf import settings
import time

User = get_user_model()

class PerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test movies
        self.movies = []
        for i in range(20):
            movie = Movie.objects.create(
                title=f'Test Movie {i}',
                director=f'Director {i}',
                release_year=2000 + i,
                description=f'Description {i}',
                runtime=90 + i,
                country='Test Country',
                movement='Test Movement'
            )
            self.movies.append(movie)

    def test_movie_list_performance(self):
        url = reverse('movies:movie-list')
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 5)  # Ensure efficient querying

    def test_movie_detail_with_related_data(self):
        url = reverse('movies:movie-detail', kwargs={'slug': self.movies[0].slug})
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 5)  # Ensure efficient querying

    def test_api_list_performance(self):
        url = reverse('movies-api:movie-list')
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 5)  # Ensure efficient querying

    def test_cache_effectiveness(self):
        url = reverse('movies:movie-list')
        cache.clear()  # Clear cache before testing
        
        # First request - should hit the database
        with CaptureQueriesContext(connection) as context:
            response1 = self.client.get(url)
            queries_first_request = len(context.captured_queries)
        
        # Second request - should use cache
        with CaptureQueriesContext(connection) as context:
            response2 = self.client.get(url)
            queries_second_request = len(context.captured_queries)
        
        self.assertLess(queries_second_request, queries_first_request)

    def test_pagination_performance(self):
        url = reverse('movies-api:movie-list')
        
        # Create more test data
        for i in range(50):
            Movie.objects.create(
                title=f'Pagination Test Movie {i}',
                director=f'Director {i}',
                release_year=2000 + i,
                description=f'Description {i}',
                runtime=90 + i,
                country='Test Country',
                movement='Test Movement'
            )
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 5)  # Ensure efficient querying
            self.assertTrue('results' in response.data)
            self.assertLessEqual(len(response.data['results']), settings.REST_FRAMEWORK.get('PAGE_SIZE', 10))

    def test_search_performance_with_complex_filters(self):
        url = reverse('movies-api:movie-list')
        filters = {
            'search': 'Test',
            'release_year': 2010,
            'movement': 'Test Movement',
            'ordering': '-average_rating'
        }
        
        with CaptureQueriesContext(connection) as context:
            start_time = time.time()
            response = self.client.get(url, filters)
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 5)  # Ensure efficient querying
            self.assertLess(end_time - start_time, 0.5)  # Response time under 500ms

    def test_related_data_loading_performance(self):
        url = reverse('movies-api:movie-detail', kwargs={'slug': self.movies[0].slug})
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(context.captured_queries), 5)  # Ensure efficient querying

    def test_database_query_optimization(self):
        # Test that indexes are being used effectively
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tablename, indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename LIKE 'movies_%'
            """)
            indexes = cursor.fetchall()
            
            # Verify essential indexes exist
            index_columns = [idx[2] for idx in indexes]
            self.assertTrue(any('title' in idx for idx in index_columns))
            self.assertTrue(any('release_year' in idx for idx in index_columns))
            self.assertTrue(any('director' in idx for idx in index_columns))
            self.assertTrue(any('movement' in idx for idx in index_columns))
            self.assertTrue(any('average_rating' in idx for idx in index_columns))