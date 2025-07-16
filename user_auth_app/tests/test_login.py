from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="pw")
        self.client = APIClient()

    def test_successful_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'pw'
        }
        response = self.client.post(url, data, format='json')
        expected_response = {
            'token': Token.objects.get(user=self.user).key,
            'username': self.user.username,
            'email': self.user.email,
            'user_id': self.user.id,
        }
        self.assertEqual(response.data, expected_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Invalid credentials.',
                      response.data['non_field_errors'])

    def test_login_with_nonexistent_username(self):
        url = reverse('login')
        data = {
            'username': 'doesnotexist',
            'password': 'any'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('User with this username does not exist.',
                      response.data['non_field_errors'])

    def test_login_missing_username(self):
        url = reverse('login')
        data = {
            'password': 'pw'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('This field is required.', response.data['username'])
    
    def test_login_missing_password(self):
        url = reverse('login')
        data = {
            'username': 'password'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('This field is required.', response.data['password'])