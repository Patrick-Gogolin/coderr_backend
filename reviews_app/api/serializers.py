from rest_framework import serializers
from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','business_user','reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        user = self.context['request'].user
        business_user = attrs['business_user']

        already_reviewed = Review.objects.filter(business_user = business_user, reviewer=user).exists()
        if already_reviewed:
            raise serializers.ValidationError("You have already reviewed this business user.")
        return attrs

    def validate_rating(self, value):
        if not 1 <= value <=5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
        
    def validate_business_user(self, value):
        print(value.userprofile)
        print(self.context['request'].user)
        if value.userprofile.type != 'business':
            raise serializers.ValidationError("The user must be a business user.")
        return value