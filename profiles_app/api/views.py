from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, CustomerProfileListSerializer, BusinessProfileListSerializer
from .permissions import IsOwnerOfProfile


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfProfile]

class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')

class BusinessProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='business')