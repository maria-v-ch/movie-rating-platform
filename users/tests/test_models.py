from django.contrib.auth import get_user_model
from django.test import TestCase

from movies.models import Movie
from users.models import UserFavoriteMovie

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123", bio="Test bio"
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

    def test_user_creation(self):
        """Test user creation with all fields"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.bio, "Test bio")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_str(self):
        """Test string representation of user"""
        self.assertEqual(str(self.user), "testuser")

    def test_user_favorite_movie_creation(self):
        """Test creating a user favorite movie relationship"""
        favorite = UserFavoriteMovie.objects.create(user=self.user, movie=self.movie)
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.movie, self.movie)
        self.assertTrue(self.user.favorite_movies.filter(id=self.movie.id).exists())

    def test_user_favorite_movie_uniqueness(self):
        """Test that a user can't favorite the same movie twice"""
        UserFavoriteMovie.objects.create(user=self.user, movie=self.movie)
        with self.assertRaises(Exception):
            UserFavoriteMovie.objects.create(user=self.user, movie=self.movie)

    def test_user_favorite_movies_deletion(self):
        """Test that favorite relationships are deleted with the user"""
        UserFavoriteMovie.objects.create(user=self.user, movie=self.movie)
        self.user.delete()
        self.assertFalse(UserFavoriteMovie.objects.filter(movie=self.movie).exists())

    def test_user_profile_fields(self):
        """Test user profile fields"""
        # Test default values
        user = User.objects.create_user(username="defaultuser", email="default@example.com", password="defaultpass123")
        self.assertEqual(user.bio, "")
        self.assertFalse(bool(user.profile_image))  # Profile image should be empty by default

        # Test setting profile fields
        user.bio = "New bio"
        user.profile_image = "profile.jpg"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.bio, "New bio")
        self.assertEqual(str(user.profile_image), "profile.jpg")
