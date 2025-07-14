from reviews_app.api.serializers import ReviewSerializer, UpdateReviewSerializer
from reviews_app.models import Review
from rest_framework import generics
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ReviewViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]
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
        if getattr(user, 'userprofile', None) is None or user.userprofile.type != 'customer':
            raise PermissionDenied("Only Customers can create reviews.")
        serializer.save(reviewer=user)
    
    def get_serializer_class(self):
        if self.action == 'partial_update' or self.action == 'update':
            return UpdateReviewSerializer
        return ReviewSerializer