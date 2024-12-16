from django.test import TestCase, Client
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework.test import force_authenticate

User = get_user_model()

class SecurityTests(APITestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.django_client = Client(enforce_csrf_checks=True)
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'terms': True
        }

    def test_csrf_protection_on_registration(self):
        """Test that registration requires CSRF token"""
        # Try without CSRF token
        response = self.django_client.post(reverse('users:register'), self.user_data)
        self.assertEqual(response.status_code, 403)
        
        # Get CSRF token
        response = self.django_client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        csrf_token = get_token(response.wsgi_request)
        
        # Try with CSRF token
        self.django_client.cookies['csrftoken'] = csrf_token
        response = self.django_client.post(
            reverse('users:register'),
            self.user_data,
            HTTP_X_CSRFTOKEN=csrf_token
        )
        # Check either for redirect (302) or successful registration (200)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            # If it's 200, make sure the user was actually created
            self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_csrf_protection_on_login(self):
        """Test that login requires CSRF token"""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Try without CSRF token
        response = self.django_client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 403)
        
        # Get CSRF token
        response = self.django_client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        csrf_token = get_token(response.wsgi_request)
        
        # Try with CSRF token
        self.django_client.cookies['csrftoken'] = csrf_token
        response = self.django_client.post(
            reverse('users:login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            HTTP_X_CSRFTOKEN=csrf_token
        )
        self.assertEqual(response.status_code, 302)  # Successful login redirects

    def test_xss_prevention(self):
        """Test that XSS attempts are prevented"""
        # Create a test user and authenticate
        user = User.objects.create_superuser(
            username='xss_test_user',
            email='xss_test@example.com',
            password='testpass123'
        )

        # Get CSRF token and set up session
        self.client.force_authenticate(user=user)
        session = self.client.session
        session.save()
        
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
        
        # Make the request
        response = self.client.post(
            '/api/v1/movies/',
            data,
            format='json'
        )

        # Should be rejected with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('HTML tags are not allowed', str(response.data))

        # Try to create a movie with safe data
        data['title'] = 'Safe Movie Title'
        response = self.client.post('/api/v1/movies/', data, format='json')
        
        # Should be created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Safe Movie Title') 