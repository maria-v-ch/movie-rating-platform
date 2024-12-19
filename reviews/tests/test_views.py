from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from movies.models import Movie
from reviews.models import Rating, Review
from reviews.permissions import IsOwnerOrReadOnly

User = get_user_model()


class IsOwnerOrReadOnlyTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
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
        self.review = Review.objects.create(user=self.user, movie=self.movie, text="Great movie!")
        self.permission = IsOwnerOrReadOnly()

    def test_safe_methods(self):
        request = Request(self.factory.get("/"))
        request.user = AnonymousUser()
        self.assertTrue(self.permission.has_object_permission(request, None, self.review))

    def test_unsafe_methods(self):
        # Test owner
        request = Request(self.factory.delete("/"))
        request.user = self.user
        self.assertTrue(self.permission.has_object_permission(request, None, self.review))

        # Test non-owner
        request = Request(self.factory.delete("/"))
        request.user = self.other_user
        self.assertFalse(self.permission.has_object_permission(request, None, self.review))


class BaseTestCase(APITestCase):
    def setUp(self):
        # Clean up any existing data
        Rating.objects.all().delete()
        Review.objects.all().delete()
        Movie.objects.all().delete()
        User.objects.all().delete()

        # Create fresh test data
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2023,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
        )

    def authenticate(self, user=None):
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")


class ReviewViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.review_data = {"movie_id": None, "text": "Great movie!", "score": 4.5}  # Will be set after super().setUp()
        self.review_url = reverse("reviews:review-list")
        self.review_data["movie_id"] = self.movie.id

    def test_list_reviews(self):
        Review.objects.create(user=self.user, movie=self.movie, text="Test review")
        response = self.client.get(f"{self.review_url}?movie={self.movie.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_review(self):
        # Try without authentication
        response = self.client.post(self.review_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try with authentication
        self.authenticate()
        response = self.client.post(self.review_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_duplicate_review(self):
        self.authenticate()
        # Create first review
        response = self.client.post(self.review_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to create second review for same movie
        response = self.client.post(self.review_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have already reviewed this movie", str(response.data))

    def test_create_review_validation(self):
        self.authenticate()
        invalid_data = {"movie_id": self.movie.id}  # Missing text
        response = self.client.post(self.review_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RatingViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.rating_data = {"movie_id": None, "score": 4.5}  # Will be set after super().setUp()
        self.rating_url = reverse("reviews:rating-list")
        self.rating_data["movie_id"] = self.movie.id

    def test_list_ratings(self):
        Rating.objects.create(user=self.user, movie=self.movie, score=4.5)
        response = self.client.get(f"{self.rating_url}?movie_id={self.movie.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_rating(self):
        # Try without authentication
        response = self.client.post(self.rating_url, self.rating_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try with authentication
        self.authenticate()
        response = self.client.post(self.rating_url, self.rating_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)

    def test_update_existing_rating(self):
        self.authenticate()
        # Create initial rating
        response = self.client.post(self.rating_url, self.rating_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update with new rating
        self.rating_data["score"] = 3.5
        response = self.client.post(self.rating_url, self.rating_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify only one rating exists but score is updated
        self.assertEqual(Rating.objects.count(), 1)
        rating = Rating.objects.first()
        self.assertEqual(rating.score, Decimal("3.5"))

    def test_rating_validation(self):
        self.authenticate()
        invalid_data = {"movie_id": self.movie.id}  # Missing score
        response = self.client.post(self.rating_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_movie_average_rating_update(self):
        self.authenticate()
        # Create rating
        response = self.client.post(self.rating_url, self.rating_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create another user and rating
        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="testpass123")
        self.authenticate(other_user)
        self.rating_data["score"] = 3.5
        response = self.client.post(self.rating_url, self.rating_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check movie's average rating
        self.movie.refresh_from_db()
        expected_average = Decimal("4.0")  # (4.5 + 3.5) / 2
        self.assertEqual(self.movie.average_rating, expected_average)
