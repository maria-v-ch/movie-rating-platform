from django.test import TestCase
from django.contrib.auth import get_user_model
from movies.models import Movie
from django.utils.html import escape
from rest_framework import status
from rest_framework.test import APIClient

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
            username='adminuser',
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
            movement='Test Movement',
            slug='test-movie'
        )

    def test_get_movies_api(self):
        """Test retrieving movies through API"""
        response = self.client.get('/api/v1/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.movie.title)

    def test_get_movie_detail_api(self):
        """Test retrieving movie detail through API"""
        response = self.client.get(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.movie.title)
        self.assertEqual(response.data['description'], self.movie.description)

    def test_create_movie_with_html(self):
        """Test that HTML tags are rejected in movie data"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': '<script>alert("XSS")</script>Test Movie',
            'director': 'Test Director',
            'release_year': 2020,
            'description': '<script>alert("XSS")</script>Test Description',
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement',
            'slug': 'test-movie-2'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('HTML tags are not allowed', str(response.data))

    def test_update_movie_with_html(self):
        """Test that HTML tags are rejected in movie data"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': '<script>alert("XSS")</script>Updated Movie',
            'description': '<script>alert("XSS")</script>Updated Description'
        }
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('HTML tags are not allowed', str(response.data))

    def test_favorite_movie(self):
        """Test favoriting and unfavoriting a movie"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/v1/movies/{self.movie.slug}/favorite/'

        # Test favoriting
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'favorited')
        self.assertTrue(self.movie.favorited_by.filter(id=self.user.id).exists())

        # Test unfavoriting
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unfavorited')
        self.assertFalse(self.movie.favorited_by.filter(id=self.user.id).exists())

    def test_favorite_action_unauthenticated(self):
        """Test that favoriting requires authentication"""
        url = f'/api/v1/movies/{self.movie.slug}/favorite/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_favorite_action_admin(self):
        """Test favoriting and unfavoriting a movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/v1/movies/{self.movie.slug}/favorite/'

        # Test favoriting
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'favorited')
        self.assertTrue(self.movie.favorited_by.filter(id=self.admin_user.id).exists())

        # Test unfavoriting
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unfavorited')
        self.assertFalse(self.movie.favorited_by.filter(id=self.admin_user.id).exists())

    def test_create_movie_unauthorized(self):
        """Test that creating a movie requires admin privileges"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Movie',
            'director': 'Test Director',
            'release_year': 2020,
            'description': 'Test Description',
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement',
            'slug': 'test-movie-3'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_movie_unauthorized(self):
        """Test that updating a movie requires admin privileges"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated Movie',
            'description': 'Updated Description'
        }
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_movie_unauthorized(self):
        """Test that deleting a movie requires admin privileges"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_movie_admin(self):
        """Test that admin can delete a movie"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movie.objects.filter(slug=self.movie.slug).exists())

    def test_create_movie_success(self):
        """Test successfully creating a movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Movie',
            'director': 'New Director',
            'release_year': 2020,
            'description': 'New Description',
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement',
            'slug': 'new-movie'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Movie')
        self.assertEqual(response.data['description'], 'New Description')

    def test_update_movie_success(self):
        """Test successfully updating a movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description'
        }
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['description'], 'Updated Description')

    def test_admin_or_readonly_permission(self):
        """Test IsAdminOrReadOnly permission class"""
        # Test read operations without authentication
        response = self.client.get('/api/v1/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test write operations without authentication
        data = {'title': 'Test'}
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test write operations with regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test write operations with admin user
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Movie',
            'director': 'New Director',
            'release_year': 2020,
            'description': 'New Description',
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement',
            'slug': 'new-movie'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_movie_with_partial_data(self):
        """Test creating a movie with only some fields"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Movie',
            'director': 'New Director',
            'release_year': 2020,
            'description': 'Test Description',  # Description is required
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement'
            # slug is optional as it's auto-generated
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Movie')
        self.assertEqual(response.data['description'], 'Test Description')

    def test_update_movie_with_partial_data(self):
        """Test updating a movie with only some fields"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Updated Title'
        }
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['description'], self.movie.description)

    def test_admin_or_readonly_permission_edge_cases(self):
        """Test edge cases for IsAdminOrReadOnly permission"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test creating a movie with invalid data (should fail with 400)
        data = {
            'title': 'New Movie',
            # Missing required fields
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test updating with invalid data (should fail with 400)
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', {'release_year': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_action_edge_cases(self):
        """Test edge cases for favorite action"""
        self.client.force_authenticate(user=self.user)
        
        # Test favoriting non-existent movie
        with self.assertRaises(Movie.DoesNotExist):
            self.client.post('/api/v1/movies/non-existent-movie/favorite/')

        # Test favoriting with invalid slug format
        with self.assertRaises(Movie.DoesNotExist):
            self.client.post('/api/v1/movies/invalid@slug/favorite/')