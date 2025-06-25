from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile

class RegistrationTest(APITestCase):
    def test_registration_succcess(self):
        url = reverse('registration')
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }
        response =  self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertTrue(User.objects.filter(username=data['username']).exists())
        user = User.objects.get(username=data['username'])
        self.assertTrue(UserProfile.objects.filter(user=user, type='customer').exists())

    def test_registration_password_missmatch(self):
        url = reverse('registration')
        data = {
            "username": "exampleUsername2",
            "email": "example2@mail.de",
            "password": "pw1",
            "repeated_password": "pw2",
            "type": "business"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_registration_duplicate_username(self):
        User.objects.create_user(username="user1", email="test@web.de", password="pw")
        url = reverse('registration')
        data = {
            "username": "user1",
            "email": "dupemail@mail.de",
            "password": "pw",
            "repeated_password": "pw",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Username already exists', str(response.data))
    
    def test_registration_duplicate_email(self):
        User.objects.create_user(username="user2", email="test@web.de", password="pw")
        url = reverse('registration')
        data = {
            "username": "user3",
            "email": "test@web.de",
            "password": "pw",
            "repeated_password": "pw",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', str(response.data))