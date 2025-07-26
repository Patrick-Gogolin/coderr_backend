from rest_framework.test import APITestCase
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

        self.user_customer_one = User.objects.create(
            username='customer1', password='customer123', email="customer1@web.de")
        
        self.user_customer_two = User.objects.create(
            username='customer2', password='customer123', email="customer2@web.de")
        
        self.user_customer_three = User.objects.create(
            username='customer3', password='customer123', email="customer3@web.de")

        self.user_business = User.objects.create(
            username='business', password='business123', email="business@web.de")
        self.user_business.userprofile.type = 'business'
        self.user_business.userprofile.save()
        self.user_business.save()
        self.token_business = Token.objects.create(user=self.user_business)

        self.user_business_one = User.objects.create(
            username='business1', password='business123', email="business@web.de")
        self.user_business_one.userprofile.type = 'business'
        self.user_business_one.userprofile.save()
        self.user_business_one.save()

        self.user_business_two = User.objects.create(
            username='business2', password='business123', email="business@web.de")
        self.user_business_two.userprofile.type = 'business'
        self.user_business_two.userprofile.save()
        self.user_business_two.save()

        self.user_business_three = User.objects.create(
            username='business3', password='business123', email="business@web.de")
        self.user_business_three.userprofile.type = 'business'
        self.user_business_three.userprofile.save()
        self.user_business_three.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_customer.key)
    
    def create_review_payload(self, rating=4, description="Everything okay"):
        business_user_id = UserProfile.objects.filter(type='business').first().user_id
        return {
            "business_user": business_user_id,
            "rating": rating,
            "description": description
        }

    def test_create_review_successfull(self):
        url = reverse('review-list')
        data = self.create_review_payload()

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = Review.objects.first()
        expected_data = ReviewSerializer(review).data
        self.assertDictEqual(response.data, expected_data)
    
    def test_create_review_unauthorized(self):
        url = reverse('review-list')
        data = self.create_review_payload()

        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(Review.objects.all().count(), 0)
    
    def test_create_review_as_business_user(self):
        url = reverse('review-list')
        data = self.create_review_payload()

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
        data = self.create_review_payload()
        
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
    
    def test_get_review_list(self):
        url = reverse('review-list')
        business_users = UserProfile.objects.filter(type='business')

        for i, business_user in enumerate(business_users):
            Review.objects.create(
                reviewer=self.user_customer,
                business_user=business_user.user,
                rating=(i % 5) + 1,
                description=f"Alles super {i}"
            )
        
        response = self.client.get(url)
        reviews = Review.objects.all()
        expected_data = ReviewSerializer(reviews, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        self.assertEqual(len(response.data), business_users.count())
    
    def test_get_review_list_empty(self):
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_reviews_unauthorized(self):
        url = reverse('review-list')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
    
    def test_get_review_list_filtered_by_business_user(self):
        url = reverse('review-list')
        business_users = UserProfile.objects.filter(type='business')

        for i, business_user in enumerate(business_users):
            Review.objects.create(
                reviewer=self.user_customer,
                business_user=business_user.user,
                rating=(i % 5) + 1,
                description=f"Alles super {i}"
            )
        expected_reviews = Review.objects.filter(business_user_id=self.user_business_two.id).count()
        response = self.client.get(url, {'business_user_id': self.user_business_two.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(review['business_user'] == self.user_business_two.id for review in response.data))
        self.assertEqual(len(response.data), expected_reviews)
    
    def test_get_review_list_filtered_by_reviewer(self):
        url = reverse('review-list')
        business_users = UserProfile.objects.filter(type='business')

        for i, business_user in enumerate(business_users):
            Review.objects.create(
                reviewer=self.user_customer,
                business_user=business_user.user,
                rating=(i % 5) + 1,
                description=f"Alles super {i}"
            )
        expected_reviews = Review.objects.filter(reviewer_id=self.user_customer.id).count()
        response = self.client.get(url, {'reviewer_id': self.user_customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_reviews)
        self.assertTrue(all(review['reviewer'] == self.user_customer.id for review in response.data))
    
    def test_get_review_list_ordered_by_updated_at(self):
        url = reverse('review-list')
        business_users = UserProfile.objects.filter(type='business')

        for i, business_user in enumerate(business_users):
            Review.objects.create(
                reviewer=self.user_customer,
                business_user=business_user.user,
                rating=(i % 5) + 1,
                description=f"Alles super {i}"
            )
        response = self.client.get(url, {'ordering': '-updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_ats = [review['updated_at'] for review in response.data]
        self.assertEqual(updated_ats, sorted(updated_ats, reverse=True))
    
    def test_get_review_list_ordered_by_rating(self):
        url = reverse('review-list')
        business_user = UserProfile.objects.filter(type='business').first()

        for rating in [5,4,3,2,1]:
            Review.objects.create(
                reviewer= self.user_customer,
                business_user=business_user.user,
                rating=rating,
                description= f"Rating {rating}"
            )
        response = self.client.get(url, {'ordering': '-rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ratings = [review['rating'] for review in response.data]  
        self.assertEqual(ratings, sorted(ratings, reverse=True))
        self.assertEqual(len(ratings), 5)
    
    def test_delete_review(self):
        review = Review.objects.create(
            reviewer=self.user_customer,
            business_user=self.user_business_one,
            rating = 5,
            description= "Everything okay"
        )

        url = reverse('review-detail', kwargs={'pk': review.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Review.objects.all()), 0)
        self.assertFalse(Review.objects.filter(id=review.id).exists())
    
    def test_delete_review_unauthorized(self):
        review = Review.objects.create(
            reviewer=self.user_customer,
            business_user=self.user_business_one,
            rating = 5,
            description= "Everything okay"
        )

        self.client.credentials()
        url = reverse('review-detail', kwargs={'pk': review.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertTrue(Review.objects.filter(id=review.id).exists())
    
    def test_delete_review_not_owner(self):
        review = Review.objects.create(
            reviewer=self.user_customer,
            business_user=self.user_business_one,
            rating = 5,
            description= "Everything okay"
        )

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_business.key)
        url = reverse('review-detail', kwargs={'pk': review.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)
        self.assertTrue(Review.objects.filter(id=review.id).exists())