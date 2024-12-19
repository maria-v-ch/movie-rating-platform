"""Tests for movie view internals."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from movies.filters import MovieFilter
from movies.models import Movie
from movies.views import DirectorListView, MovementListView, MovieDetailView, MovieListView
from reviews.models import Rating, Review
from reviews.permissions import IsAdminOrReadOnly

User = get_user_model()


class ViewInternalsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )

        # Create test movies
        self.movie1 = Movie.objects.create(
            title="Movie 1",
            director="Director 1",
            release_year=2020,
            description="Test Description 1",
            runtime=120,
            country="Country 1",
            movement="Movement 1",
            average_rating=Decimal("4.5"),
            total_ratings=2,
        )

        self.movie2 = Movie.objects.create(
            title="Movie 2",
            director="Director 2",
            release_year=2021,
            description="Test Description 2",
            runtime=130,
            country="Country 2",
            movement="Movement 2",
            average_rating=Decimal("4.0"),
            total_ratings=1,
        )

    def test_movie_list_view_get_queryset(self):
        """Test MovieListView's get_queryset method with various filters"""
        view = MovieListView()

        # Test with no filters
        request = self.factory.get("/")
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [self.movie2, self.movie1])  # Ordered by release_year desc

        # Test with director filter
        request = self.factory.get("/?director=Director 1")
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [self.movie1])

        # Test with movement filter
        request = self.factory.get("/?movement=Movement 2")
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [self.movie2])

        # Test with year filter
        request = self.factory.get("/?year=2020")
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [self.movie1])

        # Test with all filters
        request = self.factory.get("/?director=Director 1&movement=Movement 1&year=2020")
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [self.movie1])

    def test_movie_list_view_get_context_data(self):
        """Test MovieListView's get_context_data method"""
        view = MovieListView()
        request = self.factory.get("/")
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data()

        # Test directors context
        self.assertIn("directors", context)
        directors = list(context["directors"])
        self.assertEqual(len(directors), 2)
        director1 = next(d for d in directors if d["director"] == "Director 1")
        self.assertEqual(director1["movie_count"], 1)

        # Test movements context
        self.assertIn("movements", context)
        movements = list(context["movements"])
        self.assertEqual(len(movements), 2)
        movement1 = next(m for m in movements if m["movement"] == "Movement 1")
        self.assertEqual(movement1["movie_count"], 1)

        # Test years context
        self.assertIn("years", context)
        years = list(context["years"])
        self.assertEqual(len(years), 2)
        self.assertIn(2020, years)
        self.assertIn(2021, years)

        # Test current filters
        self.assertEqual(context["current_director"], "")
        self.assertEqual(context["current_movement"], "")
        self.assertEqual(context["current_year"], "")

    def test_movie_detail_view_get_context_data(self):
        """Test MovieDetailView's get_context_data method"""
        # Create a review and rating
        review = Review.objects.create(movie=self.movie1, user=self.user, text="Test review")
        rating = Rating.objects.create(movie=self.movie1, user=self.user, score=Decimal("4.5"))

        view = MovieDetailView()
        request = self.factory.get("/")
        request.user = self.user
        view.request = request
        view.kwargs = {"pk": self.movie1.pk}
        view.object = self.movie1
        context = view.get_context_data()

        # Test reviews context
        self.assertIn("reviews", context)
        self.assertEqual(list(context["reviews"]), [review])

        # Test user_ratings context
        self.assertIn("user_ratings", context)
        self.assertEqual(context["user_ratings"][self.user.id], rating)

        # Test similar_movies context
        self.assertIn("similar_movies", context)
        self.assertEqual(list(context["similar_movies"]), [])  # No similar movies yet

        # Test user's review and rating
        self.assertEqual(context["user_review"], review)
        self.assertEqual(context["user_rating"], rating)

    def test_director_list_view_get_queryset(self):
        """Test DirectorListView's get_queryset method"""
        view = DirectorListView()
        request = self.factory.get("/")
        view.request = request
        queryset = view.get_queryset()
        directors = list(queryset)

        self.assertEqual(len(directors), 2)
        director1 = next(d for d in directors if d["director"] == "Director 1")
        self.assertEqual(director1["movie_count"], 1)
        self.assertEqual(director1["rated_count"], 0)
        self.assertIsNone(director1["avg_rating"])

    def test_movement_list_view_get_queryset(self):
        """Test MovementListView's get_queryset method"""
        view = MovementListView()
        request = self.factory.get("/")
        view.request = request
        queryset = view.get_queryset()
        movements = list(queryset)

        self.assertEqual(len(movements), 2)
        movement1 = next(m for m in movements if m["movement"] == "Movement 1")
        self.assertEqual(movement1["movie_count"], 1)
        self.assertEqual(movement1["rated_count"], 0)
        self.assertIsNone(movement1["avg_rating"])

    def test_movie_filter_exact_matches(self):
        """Test MovieFilter with exact matches"""
        filtered = MovieFilter(
            {"release_year": 2020, "director": "Director 1", "movement": "Movement 1"}, queryset=Movie.objects.all()
        )
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

    def test_movie_filter_case_insensitive(self):
        """Test MovieFilter case insensitivity"""
        filtered = MovieFilter({"director": "director 1", "movement": "movement 1"}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

    def test_movie_filter_no_matches(self):
        """Test MovieFilter with no matches"""
        filtered = MovieFilter(
            {"release_year": 2022, "director": "Nonexistent", "movement": "Nonexistent"}, queryset=Movie.objects.all()
        )
        self.assertEqual(filtered.qs.count(), 0)

    def test_is_admin_or_readonly_permission(self):
        """Test IsAdminOrReadOnly permission class"""
        permission = IsAdminOrReadOnly()

        # Test safe methods
        for method in ["GET", "HEAD", "OPTIONS"]:
            request = type("Request", (), {"method": method, "user": None})()
            self.assertTrue(permission.has_permission(request, None))

        # Test unsafe methods with regular user
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            request = type("Request", (), {"method": method, "user": self.user})()
            self.assertFalse(permission.has_permission(request, None))

        # Test unsafe methods with admin user
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            request = type("Request", (), {"method": method, "user": self.admin_user})()
            self.assertTrue(permission.has_permission(request, None))

        # Test unsafe methods with unauthenticated user
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            request = type("Request", (), {"method": method, "user": None})()
            self.assertFalse(permission.has_permission(request, None))
