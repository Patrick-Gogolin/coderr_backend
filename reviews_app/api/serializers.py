from rest_framework import serializers
from reviews_app.models import Review

REVIEW_FIELDS = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
READ_ONLY_COMMON = ['id', 'reviewer', 'created_at', 'updated_at']
READ_ONLY_UPDATE = READ_ONLY_COMMON + ['business_user']

class BaseReviewSerializer(serializers.ModelSerializer):
    """
    Base serializer for Review model.
    
    Fields:
        - id
        - business_user
        - reviewer
        - rating
        - description
        - created_at
        - updated_at

    Validations:
        - Ensures rating is between 1 and 5 inclusive.
    """

    class Meta:
        model = Review
        fields = REVIEW_FIELDS

    def validate_rating(self, value):
        """
        Validate that rating is between 1 and 5.
        """
        if not 1 <= value <=5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ReviewSerializer(BaseReviewSerializer):
    """
    Serializer for creating and listing reviews.

    Read-only fields:
        - id
        - reviewer
        - created_at
        - updated_at

    Validations:
        - User can only create one review per business_user.
        - business_user must have a userprofile.type of 'business'.
    """
    class Meta(BaseReviewSerializer.Meta):
        read_only_fields = READ_ONLY_COMMON
    
    def validate(self, attrs):
        """
        Validate that the current user hasn't already reviewed the business_user.
        """
        user = self.context['request'].user
        business_user = attrs['business_user']

        already_reviewed = Review.objects.filter(business_user=business_user, reviewer=user).exists()
        if already_reviewed:
            raise serializers.ValidationError("You have already reviewed this business user.")
        return attrs
        
    def validate_business_user(self, value):
        """
        Validate that business_user is actually of type 'business'.
        """
        if value.userprofile.type != 'business':
            raise serializers.ValidationError("The user must be a business user.")
        return value
    
class UpdateReviewSerializer(BaseReviewSerializer):
    """
    Serializer for updating reviews.

    Read-only fields:
        - id
        - reviewer
        - created_at
        - updated_at
        - business_user
    """
    class Meta(BaseReviewSerializer.Meta):
        read_only_fields = READ_ONLY_UPDATE