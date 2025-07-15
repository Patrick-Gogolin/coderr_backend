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
        user = self.request.user
        serializer.save(reviewer=user)
    
    def get_serializer_class(self):
        if self.action == 'partial_update' or self.action == 'update':
            return UpdateReviewSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), isUserFromTypeCustomer()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), isCreatorOfReview()]
        else:
            return [IsAuthenticated()]

class GeneralInformationView(APIView):
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
