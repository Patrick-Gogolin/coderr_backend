from rest_framework import serializers
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        exclude = ['id', 'offer']

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details'
        ]
    
    def validate(self, attrs):
        details = attrs.get('details', [])
        if len(details) < 3:
            raise serializers.ValidationError("Ein Offer muss mindestens 3 Details haben!")
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=request.user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferBaseSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    def get_details(self, obj):
        result = []
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


class OfferListSerializer(OfferBaseSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }


class OfferWithDetailsSerializer(OfferBaseSerializer):

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time'
        ]

class OfferDetailPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        extra_kwargs = {'offer_type': {'required':True}}


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailPartialUpdateSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'image', 'details']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'image': {'required': False}
        }

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
    
            existing_details = {}
            for detail in instance.details.all():
                existing_details[detail.offer_type] = detail
                
            for detail in details_data:
                offer_type = detail.get('offer_type')
                if offer_type in existing_details:
                    detail_instance = existing_details[offer_type]
                    for attr, value in detail.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    raise serializers.ValidationError(
                        f"Detail mit offer_type '{offer_type}' nicht gefunden."
                    )

        return instance