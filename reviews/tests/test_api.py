from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie
from reviews.models import Rating, Review

User = get_user_model()


class ReviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")

        # Create test movie
        self.movie = Movie.objects.create(
            title="8½",
            director="Federico Fellini",
            release_year=1963,
            description="A film about creative and personal crisis",
            runtime=138,
            country="Italy",
            movement="Italian Neorealism",
        )

        # Create a review and rating separately
        self.review = Review.objects.create(movie=self.movie, user=self.user, text="A masterpiece of cinema.")
        self.rating = Rating.objects.create(movie=self.movie, user=self.user, score=Decimal("4.5"))

    def test_create_review_authenticated(self):
        """Test creating a review when authenticated"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:review-list")
        data = {"movie_id": self.movie.id, "text": "An excellent film.", "score": "4.5"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

        # Verify review was created
        new_review = Review.objects.get(user=self.user2)
        self.assertEqual(new_review.text, "An excellent film.")

        # Verify rating was created separately
        new_rating = Rating.objects.get(user=self.user2, movie=self.movie)
        self.assertEqual(new_rating.score, Decimal("4.5"))

    def test_create_review_unauthenticated(self):
        """Test creating a review when unauthenticated fails"""
        url = reverse("reviews:review-list")
        data = {"movie_id": self.movie.id, "text": "An excellent film.", "score": "4.5"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_review_fails(self):
        """Test that a user cannot review the same movie twice"""
        self.client.force_authenticate(user=self.user)
        url = reverse("reviews:review-list")
        data = {"movie_id": self.movie.id, "text": "Another review.", "score": "4.0"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews(self):
        """Test listing reviews"""
        url = reverse("reviews:review-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        # Verify basic review data
        self.assertEqual(response.data["results"][0]["text"], "A masterpiece of cinema.")
        self.assertEqual(response.data["results"][0]["user"], self.user.username)
        self.assertEqual(response.data["results"][0]["movie"]["id"], self.movie.id)
        self.assertEqual(response.data["results"][0]["rating_score"], "4.5")

    def test_filter_reviews_by_movie(self):
        """Test filtering reviews by movie"""
        url = reverse("reviews:review-list") + f"?movie={self.movie.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["movie"]["id"], self.movie.id)

    def test_filter_reviews_by_user(self):
        """Test filtering reviews by user"""
        url = reverse("reviews:review-list") + f"?user={self.user.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["user"], self.user.username)

    def test_update_review(self):
        """Test updating a review"""
        self.client.force_authenticate(user=self.user)
        url = reverse("reviews:review-detail", args=[self.review.id])
        data = {"text": "Updated review text", "score": "4.0"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify review text was updated
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Updated review text")

        # Verify rating was updated separately
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.score, Decimal("4.0"))
        self.assertEqual(response.data["rating_score"], "4.0")

    def test_delete_review(self):
        """Test deleting a review"""
        self.client.force_authenticate(user=self.user)
        url = reverse("reviews:review-detail", args=[self.review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_update_other_user_review_fails(self):
        """Test that updating another user's review fails"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:review-detail", args=[self.review.id])
        data = {"text": "Trying to update"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RatingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")

        # Create test movie
        self.movie = Movie.objects.create(
            title="8½",
            director="Federico Fellini",
            release_year=1963,
            description="A film about creative and personal crisis",
            runtime=138,
            country="Italy",
            movement="Italian Neorealism",
        )

        # Create a rating
        self.rating = Rating.objects.create(movie=self.movie, user=self.user, score=Decimal("4.5"))

    def test_create_rating_authenticated(self):
        """Test creating a rating when authenticated"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "4.0"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 2)

    def test_create_rating_unauthenticated(self):
        """Test creating a rating when unauthenticated fails"""
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "4.0"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_existing_rating(self):
        """Test updating an existing rating"""
        self.client.force_authenticate(user=self.user)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "3.5"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.score, Decimal("3.5"))

    def test_invalid_rating_score(self):
        """Test that invalid rating scores are rejected"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "6.0"}  # Invalid score
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_movie_average_rating_update(self):
        """Test that movie's average rating is updated"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "3.5"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.0"))  # (4.5 + 3.5) / 2
        self.assertEqual(self.movie.total_ratings, 2)

    def test_filter_ratings_by_movie(self):
        """Test filtering ratings by movie"""
        url = reverse("reviews:rating-list") + f"?movie_id={self.movie.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_ratings_by_user(self):
        """Test filtering ratings by user"""
        url = reverse("reviews:rating-list") + f"?user_id={self.user.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_invalid_decimal_places(self):
        """Test that ratings with too many decimal places are rejected"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "4.55"}  # Too many decimal places
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_numeric_score(self):
        """Test that non-numeric scores are rejected"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "invalid"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_score(self):
        """Test that negative scores are rejected"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("reviews:rating-list")
        data = {"movie_id": self.movie.id, "score": "-1.0"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_rating(self):
        """Test deleting a rating"""
        self.client.force_authenticate(user=self.user)
        url = reverse("reviews:rating-detail", args=[self.rating.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Rating.objects.count(), 0)

        # Verify movie rating is updated
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("0.0"))
        self.assertEqual(self.movie.total_ratings, 0)

    def test_update_rating_via_patch(self):
        """Test updating a rating using PATCH"""
        self.client.force_authenticate(user=self.user)
        url = reverse("reviews:rating-detail", args=[self.rating.id])
        data = {"score": "3.0"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.score, Decimal("3.0"))
