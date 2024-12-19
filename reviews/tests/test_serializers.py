from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from movies.models import Movie
from reviews.models import Rating
from reviews.serializers import RatingSerializer, ReviewSerializer

User = get_user_model()


class ReviewSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
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
        self.review_data = {"movie_id": self.movie.id, "text": "Great movie!", "score": "4.5"}

    def test_review_serializer_valid_data(self):
        """Test ReviewSerializer with valid data"""
        request = Request(self.factory.post("/api/v1/reviews/"))
        request.user = self.user
        serializer = ReviewSerializer(data=self.review_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        review = serializer.save()
        self.assertEqual(review.text, "Great movie!")
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.movie, self.movie)

        # Check that rating was created
        rating = Rating.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(rating.score, Decimal("4.5"))

    def test_review_serializer_invalid_score(self):
        """Test ReviewSerializer with invalid score"""
        request = Request(self.factory.post("/api/v1/reviews/"))
        request.user = self.user

        # Test score too high
        data = self.review_data.copy()
        data["score"] = "6.0"
        serializer = ReviewSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)

        # Test score too low
        data["score"] = "-1.0"
        serializer = ReviewSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)

        # Test invalid score format
        data["score"] = "invalid"
        serializer = ReviewSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)

    def test_review_serializer_duplicate_review(self):
        """Test ReviewSerializer prevents duplicate reviews"""
        # Create first review
        request = Request(self.factory.post("/api/v1/reviews/"))
        request.user = self.user
        serializer = ReviewSerializer(data=self.review_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Try to create second review
        serializer = ReviewSerializer(data=self.review_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError) as context:
            serializer.save()
        self.assertIn("You have already reviewed this movie.", str(context.exception))

    def test_review_serializer_update(self):
        """Test ReviewSerializer update functionality"""
        # Create initial review
        request = Request(self.factory.post("/api/v1/reviews/"))
        request.user = self.user
        serializer = ReviewSerializer(data=self.review_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        review = serializer.save()

        # Update review
        update_data = {"text": "Updated review", "score": "3.5"}
        serializer = ReviewSerializer(review, data=update_data, context={"request": request}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_review = serializer.save()
        self.assertEqual(updated_review.text, "Updated review")

        # Check that rating was updated
        rating = Rating.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(rating.score, Decimal("3.5"))

    def test_review_serializer_get_rating_score(self):
        """Test ReviewSerializer get_rating_score method"""
        # Create review with rating
        request = Request(self.factory.post("/api/v1/reviews/"))
        request.user = self.user
        serializer = ReviewSerializer(data=self.review_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        review = serializer.save()

        # Test serializer output
        serializer = ReviewSerializer(review)
        self.assertEqual(serializer.data["rating_score"], "4.5")

        # Test with no rating
        Rating.objects.all().delete()
        serializer = ReviewSerializer(review)
        self.assertIsNone(serializer.data["rating_score"])


class RatingSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
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
        self.rating_data = {"movie_id": self.movie.id, "score": "4.5"}

    def test_rating_serializer_valid_data(self):
        """Test RatingSerializer with valid data"""
        request = Request(self.factory.post("/api/v1/ratings/"))
        request.user = self.user
        serializer = RatingSerializer(data=self.rating_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        rating = serializer.save()
        self.assertEqual(rating.score, Decimal("4.5"))
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.movie, self.movie)

    def test_rating_serializer_invalid_score(self):
        """Test RatingSerializer with invalid score"""
        request = Request(self.factory.post("/api/v1/ratings/"))
        request.user = self.user

        # Test score too high
        data = self.rating_data.copy()
        data["score"] = "6.0"
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)

        # Test score too low
        data["score"] = "-1.0"
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)

        # Test invalid score format
        data["score"] = "invalid"
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("score", serializer.errors)

    def test_rating_serializer_update(self):
        """Test RatingSerializer update functionality"""
        # Create initial rating
        request = Request(self.factory.post("/api/v1/ratings/"))
        request.user = self.user
        serializer = RatingSerializer(data=self.rating_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        rating = serializer.save()

        # Update rating
        update_data = {"score": "3.5"}
        serializer = RatingSerializer(rating, data=update_data, context={"request": request}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_rating = serializer.save()
        self.assertEqual(updated_rating.score, Decimal("3.5"))

    def test_rating_serializer_movie_average(self):
        """Test that RatingSerializer updates movie average rating"""
        # Create first rating
        request = Request(self.factory.post("/api/v1/ratings/"))
        request.user = self.user
        serializer = RatingSerializer(data=self.rating_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Create second user and rating
        user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        request = Request(self.factory.post("/api/v1/ratings/"))
        request.user = user2
        data = self.rating_data.copy()
        data["score"] = "3.5"
        serializer = RatingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check movie average rating
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.0"))
