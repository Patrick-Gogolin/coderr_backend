from rest_framework import serializers
from offers_app.models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        exclude = ['offer']

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=request.user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

class OfferListSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user','title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        result= []
        for detail in obj.details.all():
            item = {
                "id": detail.id,
                "url": f"/offerdetails/{detail.id}/"
            }
            result.append(item)
        return result
        
    def get_min_price(self, obj):
        prices = obj.details.values_list('price', flat=True)
        return min(prices) if prices else None
        
    def get_min_delivery_time(self, obj):
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None
        
    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

