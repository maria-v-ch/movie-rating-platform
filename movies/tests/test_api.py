from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from movies.models import Movie
from movies.serializers import MovieSerializer

User = get_user_model()

class MovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.movie = Movie.objects.create(
            title='Test Movie',
            director='Test Director',
            release_year=2020,
            description='Test Description',
            runtime=120,
            country='Test Country',
            movement='Test Movement'
        )

    def test_get_movies_list(self):
        """Test retrieving a list of movies"""
        response = self.client.get('/api/v1/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_movie_detail(self):
        """Test retrieving a specific movie"""
        response = self.client.get(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Movie')

    def test_create_movie(self):
        """Test creating a new movie"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Movie',
            'director': 'New Director',
            'release_year': 2021,
            'description': 'New Description',
            'runtime': 130,
            'country': 'New Country',
            'movement': 'New Movement'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 2)

    def test_update_movie(self):
        """Test updating a movie"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Updated Movie'}
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, 'Updated Movie')

    def test_delete_movie(self):
        """Test deleting a movie"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Movie.objects.count(), 0)

    def test_unauthorized_create(self):
        """Test that unauthorized users cannot create movies"""
        data = {
            'title': 'Unauthorized Movie',
            'director': 'Unauthorized Director',
            'release_year': 2021,
            'description': 'Unauthorized Description',
            'runtime': 130,
            'country': 'Unauthorized Country',
            'movement': 'Unauthorized Movement'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_update(self):
        """Test that unauthorized users cannot update movies"""
        data = {'title': 'Unauthorized Update'}
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_delete(self):
        """Test that unauthorized users cannot delete movies"""
        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_movies(self):
        """Test filtering movies by various criteria"""
        Movie.objects.create(
            title='Another Movie',
            director='Another Director',
            release_year=2019,
            description='Another Description',
            runtime=110,
            country='Another Country',
            movement='Another Movement'
        )

        # Test filtering by year
        url = f'/api/v1/movies/?release_year={self.movie.release_year}'
        print(f"\nTesting URL: {url}")
        response = self.client.get(url)
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.movie.title)

        # Test filtering by director
        url = f'/api/v1/movies/?director={self.movie.director}'
        print(f"\nTesting URL: {url}")
        response = self.client.get(url)
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.movie.title)

        # Test filtering by movement
        url = f'/api/v1/movies/?movement={self.movie.movement}'
        print(f"\nTesting URL: {url}")
        response = self.client.get(url)
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.movie.title) 