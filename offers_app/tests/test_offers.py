from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from offers_app.models import Offer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta


class OfferTest(APITestCase):
    def setUp(self):
        self.user_business = User.objects.create_user(
            username="testbusiness", password="testpassword", email="test@test.de")
        self.user_business.userprofile.type = 'business'
        self.user_business.userprofile.save()
        self.user_business.save()
        self.token_business = Token.objects.create(user=self.user_business)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_business.key)

        self.user_customer = User.objects.create_user(
            username="testcostumer", password="testpassword", email="test@test.com")
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

    def create_dummy_offers(self, count=5):
        url = reverse('offer-list')
        for i in range(count):
            offer_data = self.get_offer_data()
            offer_data['title'] = f"Angebot {i}"
            offer_data['description'] = f"Beschreibung {i}"
            offer_data['details'][0]['price'] = 50 + i * 10
            offer_data['details'][0]['delivery_time_in_days'] = 3 + i
            response = self.client.post(url, offer_data, format='json')
        return response

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
        self.assertEqual(
            response.data['description'], offer_data['description'])
        self.assertIsNone(response.data.get('image'))
        for i, detail in enumerate(response.data['details']):
            self.assertIn('id', detail)
            self.assertEqual(
                detail['title'], offer_data['details'][i]['title'])
            self.assertEqual(
                detail['price'], offer_data['details'][i]['price'])
            self.assertEqual(detail['revisions'],
                             offer_data['details'][i]['revisions'])
            self.assertEqual(detail['delivery_time_in_days'],
                             offer_data['details'][i]['delivery_time_in_days'])
            self.assertEqual(detail['offer_type'],
                             offer_data['details'][i]['offer_type'])
            self.assertEqual(detail['features'],
                             offer_data['details'][i]['features'])

    def test_post_offer_unauthorized(self):
        offer_data = self.get_offer_data()
        self.client.credentials()
        url = reverse('offer-list')
        response = self.client.post(url, offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_offer_as_customer(self):
        offer_data = self.get_offer_data()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
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
        self.assertEqual(response.data['non_field_errors']
                         [0], "Ein Offer muss mindestens 3 Details haben!")
        self.assertEqual(Offer.objects.count(), 0)

    def test_get_offers_no_filter(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(len(response.data['results']), 5)

    def test_get_offers_filter_by_creator(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url, {'creator_id': self.user_business.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertTrue(all(offer['user'] == self.user_business.id for offer in response.data['results']))
    
    def test_get_offers_filter_by_min_price(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url, {'min_price': 70})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(offer['min_price'] >= 70 for offer in response.data['results']))
    
    def test_get_offers_filter_by_max_delivery_time(self):
        self.create_dummy_offers()
        max_delivery_time = 4
        url = reverse('offer-list')
        response = self.client.get(url, {'max_delivery_time': max_delivery_time})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(offer['min_delivery_time'] <= max_delivery_time for offer in response.data['results']))
    
    def test_get_offers_ordering_min_price(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url, {'ordering': 'min_price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [offer['min_price'] for offer in response.data['results']]
        self.assertEqual(prices, sorted(prices))
    
    def test_get_offers_ordering_updatet_at(self):
        now = timezone.now()
        post_response = self.create_dummy_offers()
        for i in range(5):
            offer = Offer.objects.get(id=post_response.data['id'])
            offer.updated_at = now - timedelta(days=i)
            offer.save()
        url = reverse('offer-list')
        response = self.client.get(url, {'ordering': '-updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [offer['title'] for offer in response.data['results']]
        expected_order = ['Angebot 4', 'Angebot 3', 'Angebot 2','Angebot 1','Angebot 0']
        self.assertEqual(titles, expected_order)
    
    def test_get_offers_search_for_title(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url, {'search': 'Angebot 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any('Angebot 1' in offer['title'] for offer in response.data['results']))

    def test_get_offers_search_for_description(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url, {'search': 'Beschreibung 2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any('Beschreibung 2' in offer['description'] for offer in response.data['results']))
    
    def test_get_offers_pagination(self):
        self.create_dummy_offers()
        url = reverse('offer-list')
        response = self.client.get(url, {'page_size': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_single_offer(self):
        offer_data = self.get_offer_data()
        url = reverse('offer-list')
        post_response = self.client.post(url, offer_data, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        offer_id = post_response.data['id']
        detail_url = reverse('offer-detail', kwargs = {'pk': offer_id})
        get_response = self.client.get(detail_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        data = get_response.data
        self.assertEqual(data['id'], offer_id)
        self.assertEqual(data['title'], offer_data['title'])
        self.assertEqual(data['description'], offer_data['description'])
        self.assertEqual(data['user'], self.user_business.id)

        self.assertIn('details', data)
        self.assertIsInstance(data['details'], list)
        for detail in data['details']:
            self.assertIn('id', detail)
            self.assertIn('url', detail)
        
        self.assertIn('min_price', data)
        self.assertIn('min_delivery_time', data)
    
    def test_get_single_offer_returns_404_for_nonexistent_offer(self):
        offer_id = 99999999999
        detail_url = reverse('offer-detail', kwargs = {'pk': offer_id})
        get_response = self.client.get(detail_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(str(get_response.data['detail']), "No Offer matches the given query.")
    
    def test_get_single_offer_unauthorized(self):
        offer_id = 99999999999
        self.client.credentials()
        detail_url = reverse('offer-detail', kwargs = {'pk': offer_id})
        get_response = self.client.get(detail_url)
        self.assertEqual(get_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def create_offer_and_get_detail_url(self):
        offer_data = self.get_offer_data()
        list_url = reverse('offer-list')
        post_response = self.client.post(list_url, offer_data, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        offer_id = post_response.data['id']
        detail_url = reverse('offer-detail', kwargs={'pk': offer_id})
        return offer_id, detail_url

    def test_delete_single_offer(self):
        offer_id, detail_url = self.create_offer_and_get_detail_url()
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=offer_id).exists())
    
    def test_delete_single_offer_unauthorized(self):
        offer_id, detail_url = self.create_offer_and_get_detail_url()
        self.client.credentials()
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_delete_single_offer_not_owner(self):
        offer_id, detail_url = self.create_offer_and_get_detail_url()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(pk=offer_id).exists())
    

    def test_update_single_offer(self):
        offer_id, detail_url = self.create_offer_and_get_detail_url()

        patch_data = {
            'title': 'Geändertes Angebot',
            'description': 'Neue Beschreibung',
            "details": [
                {
                    "title": "Updated-Basic-Paket",
                    "revisions": 5,
                    "delivery_time_in_days": 2,
                    "price": 102,
                    "features": ["Feature A", "Feature B"],
                    "offer_type": "basic"
                }
            ]
        }

        patch_response = self.client.patch(detail_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['title'], patch_data['title'])
        self.assertEqual(patch_response.data['description'], patch_data['description'])
        self.assertEqual(patch_response.data['details'][0], patch_data['details'][0])
    
    def test_update_single_offer_not_found(self):
        detail_url = reverse('offer-detail', kwargs={'pk': 999999999999})

        patch_data = {
            'title': 'Geändertes Angebot',
            'description': 'Neue Beschreibung',
        }
        patch_response = self.client.patch(detail_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_single_offer_unauthorized(self):
        offer_id, detail_url = self.create_offer_and_get_detail_url()
        
        patch_data = {
            'title': 'Geändertes Angebot',
            'description': 'Neue Beschreibung',
        }

        self.client.credentials()
        patch_response = self.client.patch(detail_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_single_offer_not_owner(self):
        offer_id, detail_url = self.create_offer_and_get_detail_url()

        patch_data = {
            'title': 'Geändertes Angebot',
            'description': 'Neue Beschreibung',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
        patch_response = self.client.patch(detail_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission', str(patch_response.data['detail']).lower())
        offer = Offer.objects.get(pk=offer_id)
        self.assertNotIn(offer.title, patch_data['title'])

    def test_get_details_for_single_offer(self):
        offer_id, _ = self.create_offer_and_get_detail_url()
        offer = Offer.objects.get(pk=offer_id)
        detail_id = offer.details.first().id
        get_url = reverse('offer-details', kwargs = {'pk': detail_id})
        get_response = self.client.get(get_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], detail_id)
        self.assertTrue(len(get_response.data['features']) > 0)