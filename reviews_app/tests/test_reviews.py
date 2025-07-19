from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from rest_framework.authtoken.models import Token


class ReviewTest(APITestCase):
    def setUp(self):
        self.user_customer = User.objects.create(
            username='customer', password='customer123', email="customer@web.de")
        self.token_customer = Token.objects.create(user=self.user_customer)

        self.user_business = User.objects.create(
            username='business', password='business123', email="business@web.de")
        self.user_business.userprofile.type = 'business'
        self.user_business.userprofile.save()
        self.user_business.save()
        self.token_business = Token.objects.create(user=self.user_business)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)

    def test_create_review_successfull(self):
        url = reverse('review-list')
        business_user_id = UserProfile.objects.filter(type='business').first().user_id
        data = {
            "business_user": business_user_id,
            "rating": 4,
            "description": "Alles war toll!"
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
