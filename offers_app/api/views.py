from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from offers_app.models import Offer
from offers_app.api.serializers import OfferCreateSerializer, OfferListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from offers_app.api.permissions import IsTypeBusiness

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsTypeBusiness]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer
    
    def get_queryset(self):
        queryset = Offer.objects.all()

        content_param = self.request.query_params.get('creator_id', None)
        if content_param is not None:
            queryset = queryset.filter(user_id=content_param)
        
        min_price_param = self.request.query_params.get('min_price', None)
        if min_price_param is not None:
            queryset = queryset.filter(details__price__gte=min_price_param)
        
        
        return queryset.distinct()