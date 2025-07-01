from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from offers_app.models import Offer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class OfferTest(APITestCase):
    def setUp(self):
        self.user_business = User.objects.create_user(username="testbusiness", password="testpassword", email="test@test.de")
        self.user_business.userprofile.type = 'business'
        self.user_business.userprofile.save()
        self.user_business.save()
        self.token_business = Token.objects.create(user=self.user_business)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)

        self.user_customer = User.objects.create_user(username="testcostumer", password="testpassword", email="test@test.com")
        self.token_customer = Token.objects.create(user=self.user_customer)

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
    
    def get_offer_less_than_three_details_data(self):
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
            ]
        }
        
    def test_post_offer(self):
        offer_data = self.get_offer_data()
        url = reverse('offer-list')
        response = self.client.post(url, offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertIn('details', response.data)
        self.assertEqual(len(response.data['details']), 3)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], offer_data['title'])
        self.assertEqual(response.data['description'], offer_data['description'])
        self.assertIsNone(response.data.get('image'))
        for i, detail in enumerate(response.data['details']):
            self.assertIn('id', detail)
            self.assertEqual(detail['title'], offer_data['details'][i]['title'])
            self.assertEqual(detail['price'], offer_data['details'][i]['price'])
            self.assertEqual(detail['revisions'], offer_data['details'][i]['revisions'])
            self.assertEqual(detail['delivery_time_in_days'], offer_data['details'][i]['delivery_time_in_days'])
            self.assertEqual(detail['offer_type'], offer_data['details'][i]['offer_type'])
            self.assertEqual(detail['features'], offer_data['details'][i]['features'])
    
    def test_post_offer_unauthorized(self):
        offer_data = self.get_offer_data()
        self.client.credentials()
        url = reverse('offer-list')
        response = self.client.post(url, offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_post_offer_as_customer(self):
        offer_data = self.get_offer_data()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        url = reverse('offer-list')
        response = self.client.post(url, offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 0)
    
    def test_post_offer_less_than_three_details(self):
        offer_data = self.get_offer_less_than_three_details_data()
        url = reverse('offer-list')
        response = self.client.post(url, offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Ein Offer muss mindestens 3 Details haben!")
        self.assertEqual(Offer.objects.count(), 0)
