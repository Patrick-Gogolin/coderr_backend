from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer, OrderUpdateSerializer
from offers_app.models import Offer, OfferDetail
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class OrderTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create(username="admin", password="admin123", is_staff=True)
        self.token_admin = Token.objects.create(user=self.admin_user)

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
    
    def create_orders_for_offers(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)
        url_post = reverse('order-list')

        for offer in Offer.objects.all():
            offer_detail_id = offer.details.first().id
            data = {
                'offer_detail_id': offer_detail_id
            }
            self.client.post(url_post, data, format='json')
        
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

    def test_create_order_returns_401_without_authentication(self):
        self.create_offer_with_details()
        offer = Offer.objects.get(title="Testangebot 1")
        offer_detail = offer.details.first()
        url = reverse('order-list')
        self.client.credentials()
        data = {
            'offer_detail_id': offer_detail.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
    
    def test_create_order_returns_403_for_non_customer(self):
        self.create_offer_with_details()
        offer = Offer.objects.get(title="Testangebot 1")
        offer_detail = offer.details.first()
        data = {
            'offer_detail_id': offer_detail.id
        }
        url = reverse('order-list')
        self.client.credentials(HTTP_AUTHORIZATION= 'Token ' + self.token_business.key)
        response= self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_create_order_returns_400_for_invalid_offer_detail_id(self):
        self.create_offer_with_details()
        invalid_id = OfferDetail.objects.order_by('-id').first().id + 1
        data = {
            'offer_detail_id': invalid_id
        }
        url = reverse('order-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['offer_detail_id'][0]), 'Offer detail with this ID does not exist.')

    def test_create_order_returns_400_if_offer_detail_id_missing(self):
        url = reverse('order-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)

        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['offer_detail_id'][0]), 'This field is required.')
    
    def test_create_order_returns_400_if_offer_detail_id_is_not_integer(self):
        url = reverse('order-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)
        
        response = self.client.post(url, {'offer_detail_id': "something"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['offer_detail_id'][0]), 'A valid integer is required.')
    
    def test_get_orders(self):
        self.create_offer_with_details()
        url = reverse('order-list')
        
        self.create_orders_for_offers()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        orders = Order.objects.all()
        expected_data = OrderSerializer(orders, many=True).data
        self.assertListEqual(response.data, expected_data)
    
    def test_get_orders_unauthorized(self):
        url = reverse('order-list')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_allowed_for_admin(self):
        self.create_offer_with_details()

        self.create_orders_for_offers()

        order_id = Order.objects.first().id
        url_delete = reverse('order-detail', kwargs={'pk': order_id})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_admin.key)
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order_id).exists())
    
    def test_delete_order_forbidden_for_non_admin(self):
        self.create_offer_with_details()

        self.create_orders_for_offers()

        order_id = Order.objects.first().id
        url_delete = reverse('order-detail', kwargs={'pk': order_id})
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_unauthorized(self):
        self.create_offer_with_details()
        
        self.create_orders_for_offers()

        order_id = Order.objects.first().id 
        url_delete = reverse('order-detail', kwargs={'pk': order_id})
        self.client.credentials()
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_delete_nonexistent_order_returns_404(self):
        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_admin.key)
        url_delete = reverse('order-detail', kwargs={'pk': 9999999})
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_order_successfully(self):
        self.create_offer_with_details()

        self.create_orders_for_offers()
        order = Order.objects.first()

        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_business.key)  
        url_patch = reverse('order-detail', kwargs={'pk': order.id})
        data = {
            "status": "completed"
        }
        response = self.client.patch(url_patch, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        expected_data = OrderUpdateSerializer(order).data
        self.assertDictEqual(response.data, expected_data)
    
    def test_update_order_as_customer(self):
        self.create_offer_with_details()

        self.create_orders_for_offers()
        order = Order.objects.first()

        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_customer.key)
        url_patch = reverse('order-detail', kwargs={'pk': order.id})
        data = {
            "status": "completed"
        }
        response = self.client.patch(url_patch, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertNotEqual(order.status, "completed")

    def test_update_order_unauthorized(self):
        self.create_offer_with_details()

        self.create_orders_for_offers()
        order = Order.objects.first()

        self.client.credentials()
        url_patch = reverse('order-detail', kwargs={'pk': order.id})
        data = {
            "status": "completed"
        }
        response = self.client.patch(url_patch, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        order.refresh_from_db()
        self.assertNotEqual(order.status, "completed")

    def test_update_order_wrong_data(self):
        self.create_offer_with_details()

        self.create_orders_for_offers()
        order = Order.objects.first()

        self.client.credentials(HTTP_AUTHORIZATION = 'Token ' + self.token_business.key)
        url_patch = reverse('order-detail', kwargs={'pk': order.id})
        data = {
            "status": "something"
        }
        response = self.client.patch(url_patch, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
        self.assertIn('not a valid choice', str(response.data['status'][0]))