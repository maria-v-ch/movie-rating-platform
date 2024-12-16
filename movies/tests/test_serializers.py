from django.test import TestCase
from django.core.exceptions import ValidationError
from movies.serializers import MovieSerializer, MovieListSerializer, DirectorSerializer, MovementSerializer
from movies.models import Movie
from rest_framework.exceptions import ValidationError as DRFValidationError

class MovieSerializerTests(TestCase):
    def setUp(self):
        self.movie_data = {
            'title': 'Test Movie',
            'director': 'Test Director',
            'release_year': 2020,
            'description': 'Test Description',
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement'
        }
        self.movie = Movie.objects.create(**self.movie_data)

    def test_movie_serializer_valid_data(self):
        """Test MovieSerializer with valid data"""
        serializer = MovieSerializer(data=self.movie_data)
        self.assertTrue(serializer.is_valid())
        movie = serializer.save()
        self.assertEqual(movie.title, 'Test Movie')
        self.assertTrue(movie.slug.startswith('test-movie'))

    def test_movie_serializer_html_validation(self):
        """Test MovieSerializer HTML validation"""
        # Test HTML in title
        data = self.movie_data.copy()
        data['title'] = 'Test <script>alert("xss")</script>'
        serializer = MovieSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

        # Test HTML in description
        data = self.movie_data.copy()
        data['description'] = 'Test <script>alert("xss")</script>'
        serializer = MovieSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

        # Test HTML in director
        data = self.movie_data.copy()
        data['director'] = 'Test <script>alert("xss")</script>'
        serializer = MovieSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

        # Test HTML in movement
        data = self.movie_data.copy()
        data['movement'] = 'Test <script>alert("xss")</script>'
        serializer = MovieSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

        # Test HTML in country
        data = self.movie_data.copy()
        data['country'] = 'Test <script>alert("xss")</script>'
        serializer = MovieSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_movie_serializer_escaping(self):
        """Test MovieSerializer escaping of special characters"""
        data = self.movie_data.copy()
        data.update({
            'title': 'Test & Movie',
            'description': 'Test & Description',
            'director': 'Test & Director',
            'movement': 'Test & Movement',
            'country': 'Test & Country'
        })
        serializer = MovieSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        movie = serializer.save()
        self.assertEqual(movie.title, 'Test &amp; Movie')
        self.assertEqual(movie.description, 'Test &amp; Description')
        self.assertEqual(movie.director, 'Test &amp; Director')
        self.assertEqual(movie.movement, 'Test &amp; Movement')
        self.assertEqual(movie.country, 'Test &amp; Country')

    def test_movie_list_serializer(self):
        """Test MovieListSerializer"""
        serializer = MovieListSerializer(self.movie)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Movie')
        self.assertEqual(data['director'], 'Test Director')
        self.assertEqual(data['release_year'], 2020)
        self.assertEqual(data['slug'], 'test-movie')
        self.assertNotIn('description', data)
        self.assertNotIn('runtime', data)
        self.assertNotIn('country', data)
        self.assertNotIn('movement', data)

class DirectorSerializerTests(TestCase):
    def test_director_serializer_valid_data(self):
        """Test DirectorSerializer with valid data"""
        data = {'director': 'Test Director'}
        serializer = DirectorSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_director_serializer_html_validation(self):
        """Test DirectorSerializer HTML validation"""
        data = {'director': 'Test <script>alert("xss")</script>'}
        serializer = DirectorSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_director_serializer_escaping(self):
        """Test DirectorSerializer escaping"""
        data = {'director': 'Test & Director'}
        serializer = DirectorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = {'director': 'Test & Director'}
        serializer = DirectorSerializer(instance)
        self.assertEqual(serializer.data['director'], 'Test &amp; Director')

class MovementSerializerTests(TestCase):
    def test_movement_serializer_valid_data(self):
        """Test MovementSerializer with valid data"""
        data = {'movement': 'Test Movement'}
        serializer = MovementSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_movement_serializer_html_validation(self):
        """Test MovementSerializer HTML validation"""
        data = {'movement': 'Test <script>alert("xss")</script>'}
        serializer = MovementSerializer(data=data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_movement_serializer_escaping(self):
        """Test MovementSerializer escaping"""
        data = {'movement': 'Test & Movement'}
        serializer = MovementSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = {'movement': 'Test & Movement'}
        serializer = MovementSerializer(instance)
        self.assertEqual(serializer.data['movement'], 'Test &amp; Movement') 