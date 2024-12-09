from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from movies.models import Movie
from django.contrib.auth import get_user_model

User = get_user_model()

class MovieModelTests(TestCase):
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

    def test_str_representation(self):
        """Test the string representation of the Movie model"""
        self.assertEqual(str(self.movie), 'Test Movie (2020) - Test Director')

    def test_year_property(self):
        """Test the year property returns release_year"""
        self.assertEqual(self.movie.year, 2020)

    def test_slug_generation(self):
        """Test that slugs are generated correctly"""
        self.assertEqual(self.movie.slug, 'test-movie')
        
        # Test duplicate title handling
        movie2 = Movie.objects.create(
            title='Test Movie',
            director='Another Director',
            release_year=2021,
            description='Another Description',
            runtime=130,
            country='Another Country',
            movement='Another Movement'
        )
        self.assertNotEqual(movie2.slug, self.movie.slug)
        self.assertTrue(movie2.slug.startswith('test-movie-'))

    def test_validation_release_year(self):
        """Test release year validation"""
        # Test year before first film
        movie = Movie(
            title='Invalid Year',
            director='Director',
            release_year=1887,  # First film was in 1888
            description='Description',
            runtime=120,
            country='Country',
            movement='Movement'
        )
        with self.assertRaises(ValidationError):
            movie.full_clean()

        # Test future year
        future_year = timezone.now().year + 6
        movie.release_year = future_year
        with self.assertRaises(ValidationError):
            movie.full_clean()

    def test_validation_runtime(self):
        """Test runtime validation"""
        movie = Movie(
            title='Invalid Runtime',
            director='Director',
            release_year=2020,
            description='Description',
            runtime=0,  # Invalid runtime
            country='Country',
            movement='Movement'
        )
        with self.assertRaises(ValidationError):
            movie.full_clean()

    def test_update_rating_with_no_ratings(self):
        """Test updating rating when there are no ratings"""
        self.movie.update_rating()
        self.assertEqual(self.movie.average_rating, Decimal('0.0'))
        self.assertEqual(self.movie.total_ratings, 0)

    def test_update_rating_with_ratings(self):
        """Test updating rating with actual ratings"""
        # Create a user and add some ratings
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.movie.ratings.create(user=user, score=4.5)
        self.movie.ratings.create(
            user=User.objects.create_user(
                username='testuser2',
                email='testuser2@example.com',
                password='testpass'
            ),
            score=3.5
        )
        
        self.movie.update_rating()
        self.assertEqual(self.movie.average_rating, Decimal('4.00'))
        self.assertEqual(self.movie.total_ratings, 2)