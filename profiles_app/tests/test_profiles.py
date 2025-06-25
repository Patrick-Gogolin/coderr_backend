from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from profiles_app.api.serializers import UserProfileSerializer

class UserProfileTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@test.de")
        self.token = Token.objects.create(user=self.user)
        self.second_user = User.objects.create_user(username="seconduser", password="secondpassword", email="test@test.com")
        self.second_token = Token.objects.create(user=self.second_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_user_profile(self):
        url = reverse('profile_detail', kwargs={'pk': self.user.pk})
        expected_data = UserProfileSerializer(self.user.userprofile).data
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
    
    def test_profile_created_by_signal(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
    
    def test_unauthorized_access(self):
        self.client.credentials()
        url = reverse('profile_detail', kwargs={'pk':self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_not_found(self):
        url = reverse('profile_detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_partial_update(self):
        url = reverse('profile_detail', kwargs={'pk': self.user.pk})

        old_location = self.user.userprofile.location
        old_tel = self.user.userprofile.tel

        patch_data = {
            "email": "example@email.com",
            "location": "Hamburg"
        }

        response = self.client.patch(url, data=patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "example@email.com")
        self.assertEqual(self.user.userprofile.location, "Hamburg")
        self.assertEqual(self.user.userprofile.tel, old_tel)
        self.assertEqual(self.user.username, "testuser")
    
    def test_patch_email_from_user_existing_email(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.second_token.key)
        url = reverse('profile_detail', kwargs={'pk': self.second_user.pk})

        patch_data = {
            "email": "test@test.de"
        }

        response = self.client.patch(url, data=patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], ["This Email is already in use!"])
        self.assertIn('email', response.data)
        self.second_user.refresh_from_db()
        self.assertEqual(self.second_user.email, "test@test.com")

    def test_customer_profiles_list_only_returns_customers(self):
        customer_user = User.objects.create_user(username="customeruser", password="customerpassword", email="c1@test.de")
        business_user = User.objects.create_user(username="businessuser", password="businesspassword", email="b1@test.de")

        business_profile = business_user.userprofile
        business_profile.type = 'business'
        business_profile.save()

        url = reverse('customer_profiles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = []
        for item in response.data:
            returned_ids.append(item['user'])
        
        self.assertIn(customer_user.pk, returned_ids)
        self.assertNotIn(business_user.pk, returned_ids)

    def test_customer_profiles_list_only_returns_business(self):
        customer_user = User.objects.create_user(username='customeruser2', password='customerpassword2')
        business_user = User.objects.create_user(username='businessuser2', password='businesspassword2')

        business_profile = business_user.userprofile
        business_profile.type = 'business'
        business_profile.save()

        url = reverse('business_profiles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = []
        for item in response.data:
            returned_ids.append(item['user'])
        
        self.assertIn(business_user.pk, returned_ids)
        self.assertNotIn(customer_user.pk, returned_ids)