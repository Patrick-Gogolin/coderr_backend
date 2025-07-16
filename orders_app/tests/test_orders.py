from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from orders_app.models import Order
from offers_app.models import Offer
from orders_app.api.serializers import OrderSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class OrderTest(APITestCase):
    def setUp(self):
        self.user_business = User.objects.create_user(
            username="testbusiness", password="testpassword", email="test@test.de")
        self.user_business.userprofile.type = 'business'
        self.user_business.userprofile.save()
        self.user_business.save()
        self.token_business = Token.objects.create(user=self.user_business)

        self.user_customer = User.objects.create_user(
            username="testcostumer", password="testpassword", email="test@test.com")
        self.token_customer = Token.objects.create(user=self.user_customer)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        
    def get_offer_data(self):
         return {
            "title": "Testangebot",
            "description": "Ein Angebot für Tests",
            "details": [
                {
                    "title": "Basic-Paket",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100,
                    "features": ["Feature 1", "Feature 2"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard-Paket",
                    "revisions": 3,
                    "delivery_time_in_days": 5,
                    "price": 200,
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium-Paket",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 300,
                    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
                    "offer_type": "premium"
                }
            ]
        }
    
    def create_offer_with_details(self, count=5):
        url = reverse('offer-list')
        responses = []
        for i in range(count):
            offer_data = self.get_offer_data()
            offer_data['title'] = f"Testangebot {i+1}"
            offer_data['description'] = f"Beschreibung für Angebot {i+1}"
            offer_data['details'][0]['price'] = 50 + i * 10
            offer_data['details'][0]['delivery_time_in_days'] = 3 + i
            response = self.client.post(url, offer_data, format='json')
            responses.append(response)
        return responses
        
    def test_create_order_successfull(self):
        self.create_offer_with_details() 
        offer = Offer.objects.get(title="Testangebot 1")
        offer_detail = offer.details.first()
        url = reverse('order-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)

        data = {
            'offer_detail_id': offer_detail.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.offer_detail.id, offer_detail.id)
        