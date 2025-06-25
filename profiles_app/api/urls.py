from django.urls import path
from .views import UserProfileDetailView, UserProfileListView, BusinessProfileListView

urlpatterns = [
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='profile_detail'),
    path('profiles/customer/', UserProfileListView.as_view(), name='customer_profiles'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business_profiles'),
]