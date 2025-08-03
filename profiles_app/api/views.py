from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, CustomerProfileListSerializer, BusinessProfileListSerializer
from .permissions import IsOwnerOfProfile


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint that allows a user to retrieve or update their own user profile.

    Methods:
        - GET: Retrieve the authenticated user's profile.
        - PATCH / PUT: Update the authenticated user's profile (only allowed if the user is the owner).

    Permissions:
        - The user must be authenticated.
        - The user must be the owner of the profile to update it.
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfProfile]

class UserProfileListView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all customer profiles.

    Permissions:
        - The user must be authenticated.

    Returns:
        - List of user profiles where profile type is 'customer'.
    """

    queryset = UserProfile.objects.all()
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')

class BusinessProfileListView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all business profiles.

    Permissions:
        - The user must be authenticated.

    Returns:
        - List of user profiles where profile type is 'business'.
    """
    
    queryset = UserProfile.objects.all()
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='business')