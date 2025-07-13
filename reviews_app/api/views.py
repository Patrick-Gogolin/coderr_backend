from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if user.userprofile.type != 'customer':
            raise PermissionDenied("Only Customers can create reviews.")
        serializer.save(reviewer=user)
