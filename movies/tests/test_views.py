from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from movies.models import Movie
from movies.views import IsAdminOrReadOnly, MovieFilter

User = get_user_model()

class MovieViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Create test movies
        self.movie1 = Movie.objects.create(
            title='8½',
            director='Federico Fellini',
            release_year=1963,
            description='A film about creative and personal crisis',
            runtime=138,
            country='Italy',
            movement='Italian Neorealism'
        )
        
        self.movie2 = Movie.objects.create(
            title='Breathless',
            director='Jean-Luc Godard',
            release_year=1960,
            description='A stylish French New Wave film',
            runtime=90,
            country='France',
            movement='French New Wave'
        )

    def test_movie_list_view(self):
        """Test the movie list view"""
        response = self.client.get(reverse('movies:movie-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movie_list.html')
        self.assertContains(response, '8½')
        self.assertContains(response, 'Breathless')

    def test_movie_list_search(self):
        """Test searching in movie list view"""
        response = self.client.get(reverse('movies:movie-list') + '?search=Fellini')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '8½')
        self.assertNotContains(response, 'Breathless')

    def test_movie_list_filter_movement(self):
        """Test filtering by movement"""
        response = self.client.get(reverse('movies:movie-list') + '?movement=French+New+Wave')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Breathless')
        self.assertNotContains(response, '8½')

    def test_movie_list_filter_director(self):
        """Test filtering by director"""
        response = self.client.get(reverse('movies:movie-list') + '?director=Federico+Fellini')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '8½')
        self.assertNotContains(response, 'Breathless')

    def test_movie_list_sort(self):
        """Test sorting movies"""
        response = self.client.get(reverse('movies:movie-list') + '?sort=release_year')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        breathless_pos = content.find('Breathless')
        fellini_pos = content.find('8½')
        self.assertTrue(breathless_pos < fellini_pos)  # Breathless (1960) should appear before 8½ (1963)

    def test_movie_detail_view(self):
        """Test the movie detail view"""
        response = self.client.get(reverse('movies:movie-detail', kwargs={'slug': self.movie1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movie_detail.html')
        self.assertContains(response, '8½')
        self.assertContains(response, 'Federico Fellini')
        self.assertContains(response, 'Italian Neorealism')

    def test_movie_detail_similar_movies(self):
        """Test similar movies in detail view"""
        # Create another movie by same director
        Movie.objects.create(
            title='La Dolce Vita',
            director='Federico Fellini',
            release_year=1960,
            description='Another Fellini masterpiece',
            runtime=174,
            country='Italy',
            movement='Italian Neorealism'
        )
        
        response = self.client.get(reverse('movies:movie-detail', kwargs={'slug': self.movie1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La Dolce Vita')  # Should show up in similar movies

    def test_director_list_view(self):
        """Test the director list view"""
        response = self.client.get(reverse('movies:directors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/director_list.html')
        self.assertContains(response, 'Federico Fellini')
        self.assertContains(response, 'Jean-Luc Godard')

    def test_movement_list_view(self):
        """Test the movement list view"""
        response = self.client.get(reverse('movies:movements'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movement_list.html')
        self.assertContains(response, 'Italian Neorealism')
        self.assertContains(response, 'French New Wave')

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
            password='admin123'
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

    def test_list_movies(self):
        """Test listing movies through API"""
        response = self.client.get('/api/v1/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_movie_unauthorized(self):
        """Test creating movie without authentication"""
        data = {
            'title': 'New Movie',
            'director': 'New Director',
            'release_year': 2021,
            'description': 'New Description',
            'runtime': 110,
            'country': 'New Country',
            'movement': 'New Movement'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_as_admin(self):
        """Test creating movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Movie',
            'director': 'New Director',
            'release_year': 2021,
            'description': 'New Description',
            'runtime': 110,
            'country': 'New Country',
            'movement': 'New Movement'
        }
        response = self.client.post('/api/v1/movies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 2)

    def test_update_movie_as_admin(self):
        """Test updating movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/v1/movies/{self.movie.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, 'Updated Title')

    def test_delete_movie_as_admin(self):
        """Test deleting movie as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/v1/movies/{self.movie.slug}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Movie.objects.count(), 0)

    def test_favorite_movie(self):
        """Test favoriting a movie"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/v1/movies/{self.movie.slug}/favorite/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'favorited')
        self.assertTrue(self.movie.favorited_by.filter(id=self.user.id).exists())

        # Test unfavoriting
        response = self.client.post(f'/api/v1/movies/{self.movie.slug}/favorite/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unfavorited')
        self.assertFalse(self.movie.favorited_by.filter(id=self.user.id).exists())

    def test_movie_search(self):
        """Test movie search through API"""
        response = self.client.get('/api/v1/movies/', {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get('/api/v1/movies/', {'search': 'NonexistentMovie'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_movie_filter(self):
        """Test movie filtering through API"""
        response = self.client.get('/api/v1/movies/', {
            'movement': 'Test Movement',
            'release_year': 2020
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_movie_ordering(self):
        """Test movie ordering through API"""
        Movie.objects.create(
            title='Another Movie',
            director='Another Director',
            release_year=2019,
            description='Another Description',
            runtime=100,
            country='Another Country',
            movement='Another Movement'
        )
        
        response = self.client.get('/api/v1/movies/', {'ordering': 'release_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['release_year'], 2019)

        response = self.client.get('/api/v1/movies/', {'ordering': '-release_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['release_year'], 2020)

class PermissionTests(TestCase):
    def setUp(self):
        self.permission = IsAdminOrReadOnly()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )

    def test_admin_permissions(self):
        """Test admin user permissions"""
        request = type('Request', (), {'method': 'POST', 'user': self.admin_user})()
        self.assertTrue(self.permission.has_permission(request, None))

    def test_regular_user_permissions(self):
        """Test regular user permissions for different methods"""
        request = type('Request', (), {'method': 'POST', 'user': self.regular_user})()
        self.assertFalse(self.permission.has_permission(request, None))

        request.method = 'GET'
        self.assertTrue(self.permission.has_permission(request, None))

class MovieFilterTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title='Test Movie',
            director='Test Director',
            release_year=2020,
            description='Test Description',
            runtime=120,
            country='Test Country',
            movement='Test Movement'
        )
        self.filter = MovieFilter()

    def test_year_filter(self):
        """Test filtering by release year"""
        filtered = MovieFilter({'release_year': 2020}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)

        filtered = MovieFilter({'release_year': 2021}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 0)

    def test_movement_filter(self):
        """Test filtering by movement"""
        filtered = MovieFilter({'movement': 'Test Movement'}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)

        filtered = MovieFilter({'movement': 'Other Movement'}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 0)

    def test_director_filter(self):
        """Test filtering by director"""
        filtered = MovieFilter({'director': 'Test Director'}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)

        filtered = MovieFilter({'director': 'Other Director'}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 0) 