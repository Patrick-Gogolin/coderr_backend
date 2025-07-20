from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = Review.objects.first()
        expected_data = ReviewSerializer(review).data
        self.assertDictEqual(response.data, expected_data)
    
    def test_create_review_unauthorized(self):
        url = reverse('review-list')
        business_user_id = UserProfile.objects.filter(type='business').first().user_id
        data = {
            "business_user": business_user_id,
            "rating": 4,
            "description": "Alles war toll!"
        }
        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(Review.objects.all().count(), 0)
    
    def test_create_review_as_business_user(self):
        url = reverse('review-list')
        business_user_id = UserProfile.objects.filter(type='business').first().user_id
        data = {
            "business_user": business_user_id,
            "rating": 4,
            "description": "Alles war toll!"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        self.assertIn('permission', response.data['detail'].lower())
        self.assertFalse(Review.objects.exists())
    
    def test_create_review_for_customer_user(self):
        url = reverse ('review-list')
        customer_user_id = UserProfile.objects.filter(type='customer').first().user_id
        data = {
            "business_user": customer_user_id,
            "rating": 4,
            "description": "Alles war toll!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The user must be a business user.', response.data['business_user'])
        self.assertFalse(Review.objects.exists())
    
    def test_create_duplicate_review_fails(self):
        url = reverse('review-list')
        business_user_id = UserProfile.objects.filter(type='business').first().user_id
        data = {
            "business_user": business_user_id,
            "rating": 4,
            "description": "Alles war toll!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('already reviewed' in err for err in response.data.get("non_field_errors", []))
    
    def test_create_review_for_invalid_rating(self):
        url = reverse('review-list')
        business_user_id = UserProfile.objects.filter(type='business').first().user_id

        for invalid_rating in [10,0,-1]:

            data = {
                "business_user": business_user_id,
                "rating": invalid_rating,
                "description": "Alles war toll!"
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Rating must be between 1 and 5", response.data['rating'][0])

    def test_create_review_missing_field(self):
        url = reverse('review-list')
        data = {
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('business_user', response.data)
        self.assertIn('rating', response.data)
        self.assertIn('description', response.data)
    
    def test_create_review_for_invalid_business_user(self):
        url = reverse('review-list')
        invalid_business_user_id = UserProfile.objects.all().order_by('-user_id').first().user_id + 1
        data = {
            "business_user": invalid_business_user_id,
            "rating": 4,
            "description": "Alles war toll!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('object does not exist', response.data['business_user'][0])