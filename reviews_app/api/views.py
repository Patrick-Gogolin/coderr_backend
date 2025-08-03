from reviews_app.api.serializers import ReviewSerializer, UpdateReviewSerializer
from reviews_app.models import Review
from user_auth_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.api.permissions import isUserFromTypeCustomer, isCreatorOfReview
from rest_framework.views import APIView
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Avg
from rest_framework import status

class ReviewViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    
    """
    A viewset for listing, creating, updating, and deleting reviews.

    Features:
        - List reviews, with optional filtering by `business_user_id` or `reviewer_id`.
        - Create a new review; only authenticated users of type 'customer' can create.
        - Update or partially update reviews; only the creator (reviewer) can update.
        - Delete reviews; only the creator (reviewer) can delete.
        - Supports ordering by `updated_at` and `rating`.

    Permissions:
        - Create: authenticated customers only.
        - Update/Partial Update/Delete: authenticated creators only.
        - List and other actions: authenticated users.

    Query Parameters:
        - business_user_id: Filter reviews for a specific business user.
        - reviewer_id: Filter reviews by the reviewer.

    Serializer:
        - Uses `ReviewSerializer` for list and create actions.
        - Uses `UpdateReviewSerializer` for update actions.
    """
    
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        queryset = Review.objects.all()

        business_user_id = self.request.query_params.get('business_user_id', None)
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        
        reviewer_id = self.request.query_params.get('reviewer_id', None)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset.distinct()
    
    def perform_create(self, serializer):
        """
        Save the reviewer as the current user on creation.
        """
        user = self.request.user
        serializer.save(reviewer=user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action.
        """
        if self.action == 'partial_update' or self.action == 'update':
            return UpdateReviewSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        """
        Return the list of permissions that this view requires.
        """
        if self.action == 'create':
            return [IsAuthenticated(), isUserFromTypeCustomer()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), isCreatorOfReview()]
        else:
            return [IsAuthenticated()]

class GeneralInformationView(APIView):
    """
    API endpoint that provides general statistics about reviews, business profiles, and offers.

    Permissions:
        - AllowAny: accessible to all users (authenticated or not).

    Response Data:
        - review_count: Total number of reviews.
        - average_rating: Average rating across all reviews (0 if none).
        - business_profile_count: Total number of business user profiles.
        - offer_count: Total number of offers.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(average_rating=Avg('rating'))['average_rating'] or 0
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        return Response({
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }, status=status.HTTP_200_OK)
