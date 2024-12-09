from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class SecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_xss_prevention(self):
        """Test that XSS attempts are prevented"""
        # Create a test user and authenticate
        user = User.objects.create_user(
            username='xss_test_user',
            email='xss_test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)

        # Attempt to create a movie with XSS payload
        data = {
            'title': '<script>alert("XSS")</script>',
            'director': 'Test Director',
            'release_year': 2020,
            'description': 'Test Description',
            'runtime': 120,
            'country': 'Test Country',
            'movement': 'Test Movement'
        }
        response = self.client.post('/api/v1/movies/', data, format='json')

        # Should be rejected with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('HTML tags are not allowed', str(response.data))

        # Try to create a movie with safe data
        data['title'] = 'Safe Movie Title'
        response = self.client.post('/api/v1/movies/', data, format='json')
        
        # Should be created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Safe Movie Title') 