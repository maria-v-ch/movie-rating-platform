import threading
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase

from movies.models import Movie
from reviews.models import Rating, Review

User = get_user_model()


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
        )

    def test_review_creation_integrity(self):
        """Test review creation with all required fields"""
        review = Review.objects.create(user=self.user, movie=self.movie, text="Test review text")
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.movie, self.movie)
        self.assertEqual(review.text, "Test review text")

    def test_review_unique_constraint(self):
        """Test that a user can't review the same movie twice"""
        Review.objects.create(user=self.user, movie=self.movie, text="First review")
        with self.assertRaises(IntegrityError):
            Review.objects.create(user=self.user, movie=self.movie, text="Second review")

    def test_cascade_deletion_user(self):
        """Test that reviews are deleted when user is deleted"""
        review = Review.objects.create(user=self.user, movie=self.movie, text="Test review")
        self.user.delete()
        self.assertEqual(Review.objects.filter(id=review.id).count(), 0)

    def test_cascade_deletion_movie(self):
        """Test that reviews are deleted when movie is deleted"""
        review = Review.objects.create(user=self.user, movie=self.movie, text="Test review")
        self.movie.delete()
        self.assertEqual(Review.objects.filter(id=review.id).count(), 0)


class ReviewTransactionTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
        )

    def test_concurrent_review_creation(self):
        """Test concurrent review creation for the same user and movie"""

        def create_review():
            try:
                with transaction.atomic():
                    Review.objects.create(user=self.user, movie=self.movie, text="Concurrent review")
            except IntegrityError:
                pass

        thread1 = threading.Thread(target=create_review)
        thread2 = threading.Thread(target=create_review)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Only one review should exist
        self.assertEqual(Review.objects.filter(user=self.user, movie=self.movie).count(), 1)

    def test_review_rating_update_integrity(self):
        """Test that movie rating is updated correctly when reviews change"""
        # Create initial rating
        rating1 = Rating.objects.create(user=self.user, movie=self.movie, score=Decimal("4.0"))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.0"))

        # Create second rating with different user
        user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        rating2 = Rating.objects.create(user=user2, movie=self.movie, score=Decimal("5.0"))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.5"))

        # Update first rating
        rating1.score = Decimal("3.0")
        rating1.save()
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.0"))

        # Delete second rating
        rating2.delete()
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("3.0"))


class RatingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
        )

    def test_rating_creation_integrity(self):
        """Test rating creation with all required fields"""
        rating = Rating.objects.create(user=self.user, movie=self.movie, score=4.5)
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.movie, self.movie)
        self.assertEqual(rating.score, Decimal("4.5"))

    def test_rating_unique_constraint(self):
        """Test that a user can't rate the same movie twice"""
        Rating.objects.create(user=self.user, movie=self.movie, score=4.5)
        with self.assertRaises(IntegrityError):
            Rating.objects.create(user=self.user, movie=self.movie, score=3.5)

    def test_rating_cascade_deletion(self):
        """Test cascade deletion behavior"""
        rating = Rating.objects.create(user=self.user, movie=self.movie, score=4.5)
        rating_id = rating.id

        # Test user deletion
        self.user.delete()
        self.assertFalse(Rating.objects.filter(id=rating_id).exists())

        # Create new rating for movie deletion test
        new_user = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        new_rating = Rating.objects.create(user=new_user, movie=self.movie, score=4.5)
        new_rating_id = new_rating.id

        # Test movie deletion
        self.movie.delete()
        self.assertFalse(Rating.objects.filter(id=new_rating_id).exists())

    def test_rating_score_validation(self):
        """Test rating score constraints"""
        # Test score below minimum
        rating = Rating(user=self.user, movie=self.movie, score=Decimal("-0.1"))
        self.assertEqual(rating.score, Decimal("-0.1"))
        with self.assertRaises(ValidationError):
            rating.full_clean()

        # Test score above maximum
        rating = Rating(user=self.user, movie=self.movie, score=Decimal("5.1"))
        self.assertEqual(rating.score, Decimal("5.1"))
        with self.assertRaises(ValidationError):
            rating.full_clean()

        # Test invalid decimal places
        rating = Rating(user=self.user, movie=self.movie, score=Decimal("4.55"))
        self.assertEqual(rating.score, Decimal("4.55"))
        with self.assertRaises(ValidationError):
            rating.full_clean()

        # Test valid scores
        valid_scores = [
            Decimal("0.0"),
            Decimal("0.5"),
            Decimal("1.0"),
            Decimal("2.5"),
            Decimal("3.0"),
            Decimal("4.5"),
            Decimal("5.0"),
        ]
        for score in valid_scores:
            rating = Rating.objects.create(
                user=User.objects.create_user(
                    username=f"testuser{score}", email=f"test{score}@example.com", password="testpass123"
                ),
                movie=self.movie,
                score=score,
            )
            self.assertEqual(rating.score, score)

    def test_rating_update_movie_stats(self):
        """Test that movie stats are updated correctly when ratings change"""
        # Create initial rating
        rating1 = Rating.objects.create(user=self.user, movie=self.movie, score=Decimal("4.5"))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.5"))
        self.assertEqual(self.movie.total_ratings, 1)
        self.assertEqual(rating1.score, Decimal("4.5"))

        # Add second rating
        user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        rating2 = Rating.objects.create(user=user2, movie=self.movie, score=Decimal("3.5"))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.0"))
        self.assertEqual(self.movie.total_ratings, 2)
        self.assertEqual(rating2.score, Decimal("3.5"))

        # Update first rating
        rating1.score = Decimal("5.0")
        rating1.save()
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.25"))

        # Delete second rating
        rating2.delete()
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("5.0"))
        self.assertEqual(self.movie.total_ratings, 1)


class RatingTransactionTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.movie = Movie.objects.create(
            title="Test Movie",
            director="Test Director",
            release_year=2020,
            description="Test Description",
            runtime=120,
            country="Test Country",
            movement="Test Movement",
        )

    def test_concurrent_rating_creation(self):
        """Test concurrent rating creation for the same user and movie"""

        def create_rating():
            try:
                with transaction.atomic():
                    Rating.objects.create(user=self.user, movie=self.movie, score=4.5)
            except IntegrityError:
                pass

        thread1 = threading.Thread(target=create_rating)
        thread2 = threading.Thread(target=create_rating)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Only one rating should exist
        self.assertEqual(Rating.objects.filter(user=self.user, movie=self.movie).count(), 1)

    def test_rating_update_movie_stats(self):
        """Test that movie stats are updated correctly when ratings change"""
        # Create initial rating
        rating1 = Rating.objects.create(user=self.user, movie=self.movie, score=Decimal("4.5"))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.5"))
        self.assertEqual(self.movie.total_ratings, 1)
        self.assertEqual(rating1.score, Decimal("4.5"))

        # Add second rating
        user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        rating2 = Rating.objects.create(user=user2, movie=self.movie, score=Decimal("3.5"))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.0"))
        self.assertEqual(self.movie.total_ratings, 2)
        self.assertEqual(rating2.score, Decimal("3.5"))

        # Update first rating
        rating1.score = Decimal("5.0")
        rating1.save()
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("4.25"))

        # Delete second rating
        rating2.delete()
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.average_rating, Decimal("5.0"))
        self.assertEqual(self.movie.total_ratings, 1)
