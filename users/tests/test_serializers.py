from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from movies.models import Movie
from reviews.models import Review, Rating
from decimal import Decimal
from users.models import UserFavoriteMovie

User = get_user_model()

class UserSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
        # Create some reviews and ratings
        self.review = Review.objects.create(
            user=self.user,
            movie=self.movie,
            text='Great movie!'
        )
        self.rating = Rating.objects.create(
            user=self.user,
            movie=self.movie,
            score=Decimal('4.5')
        )
        # Add movie to favorites
        UserFavoriteMovie.objects.create(user=self.user, movie=self.movie)

    def test_user_serializer(self):
        """Test the UserSerializer"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertIn('date_joined', data)
        self.assertEqual(len(data['favorite_movies']), 1)
        self.assertEqual(data['favorite_movies'][0]['title'], 'Test Movie')
        self.assertEqual(data['total_reviews'], 1)
        self.assertEqual(data['average_rating_given'], 4.5)

class UserCreateSerializerTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }

    def test_create_user_valid_data(self):
        """Test creating a user with valid data"""
        serializer = UserCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpass123'))

    def test_create_user_password_mismatch(self):
        """Test validation when passwords don't match"""
        data = self.valid_data.copy()
        data['password2'] = 'wrongpass'
        serializer = UserCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Passwords must match', str(serializer.errors['non_field_errors']))

    def test_create_user_duplicate_username(self):
        """Test validation with duplicate username"""
        User.objects.create_user(
            username='newuser',
            email='existing@example.com',
            password='existingpass123'
        )
        
        serializer = UserCreateSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

class UserUpdateSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.request = self.factory.patch('/fake-url/')
        self.request.user = self.user

    def test_update_email_valid(self):
        """Test updating email with valid data"""
        serializer = UserUpdateSerializer(
            self.user,
            data={'email': 'newemail@example.com'},
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'newemail@example.com')

    def test_update_email_duplicate(self):
        """Test validation when email is already in use"""
        serializer = UserUpdateSerializer(
            self.user,
            data={'email': 'other@example.com'},
            context={'request': self.request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('user with this email address already exists', str(serializer.errors['email'])) 