from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from movies.models import Movie
from movies.views import IsAdminOrReadOnly, MovieFilter

User = get_user_model()


class IsAdminOrReadOnlyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminOrReadOnly()
        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="regular123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )

    def test_safe_methods_allowed_for_all(self):
        """Test that safe methods (GET, HEAD, OPTIONS) are allowed for all users"""
        safe_methods = ["GET", "HEAD", "OPTIONS"]
        for method in safe_methods:
            request = self.factory.generic(method, "/api/movies/")
            request.user = None
            self.assertTrue(self.permission.has_permission(request, None))

    def test_unsafe_methods_require_admin(self):
        """Test that unsafe methods require admin privileges"""
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        for method in unsafe_methods:
            # Test with regular user
            request = self.factory.generic(method, "/api/movies/")
            request.user = self.regular_user
            self.assertFalse(self.permission.has_permission(request, None))

            # Test with admin user
            request = self.factory.generic(method, "/api/movies/")
            request.user = self.admin_user
            self.assertTrue(self.permission.has_permission(request, None))

    def test_unsafe_methods_deny_anonymous(self):
        """Test that unsafe methods are denied for anonymous users"""
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        for method in unsafe_methods:
            request = self.factory.generic(method, "/api/movies/")
            request.user = None
            self.assertFalse(self.permission.has_permission(request, None))


class MovieFilterTests(TestCase):
    def setUp(self):
        self.movie1 = Movie.objects.create(
            title="Movie 1",
            director="Director A",
            release_year=2020,
            description="Description 1",
            runtime=120,
            country="Country 1",
            movement="Movement X",
        )
        self.movie2 = Movie.objects.create(
            title="Movie 2",
            director="Director B",
            release_year=2021,
            description="Description 2",
            runtime=130,
            country="Country 2",
            movement="Movement Y",
        )

    def test_filter_by_release_year(self):
        """Test filtering movies by release year"""
        filtered = MovieFilter({"release_year": 2020}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

    def test_filter_by_movement(self):
        """Test filtering movies by movement"""
        filtered = MovieFilter({"movement": "Movement X"}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

    def test_filter_by_director(self):
        """Test filtering movies by director"""
        filtered = MovieFilter({"director": "Director B"}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie2)

    def test_filter_case_insensitive(self):
        """Test that filtering is case insensitive"""
        filtered = MovieFilter({"movement": "movement x"}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

        filtered = MovieFilter({"director": "director a"}, queryset=Movie.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

    def test_multiple_filters(self):
        """Test applying multiple filters"""
        filtered = MovieFilter(
            {"release_year": 2020, "movement": "Movement X", "director": "Director A"}, queryset=Movie.objects.all()
        )
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.movie1)

    def test_no_matches(self):
        """Test filtering with no matches"""
        filtered = MovieFilter(
            {"release_year": 2022, "movement": "Non-existent", "director": "Nobody"}, queryset=Movie.objects.all()
        )
        self.assertEqual(filtered.qs.count(), 0)
