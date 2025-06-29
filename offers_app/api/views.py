from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from offers_app.models import Offer
from offers_app.api.serializers import OfferCreateSerializer, OfferListSerializer, OfferDetailSerializer, OfferUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from offers_app.api.permissions import IsTypeBusiness, IsOwner
from django.db.models import Min, Max

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6

class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsTypeBusiness | IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at']
    pagination_class = LargeResultsSetPagination
       
    def get_queryset(self):
        queryset = Offer.objects.all()

        queryset = queryset.annotate(min_price=Min('details__price'))

        creator_id = self.request.query_params.get('creator_id', None)
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        
        min_price_param = self.request.query_params.get('min_price', None)
        if min_price_param:
            queryset = queryset.annotate(min_detail_price=Min('details__price')).filter(min_detail_price__gte=min_price_param)
        
        max_delivery_time_param = self.request.query_params.get('max_delivery_time', None)
        if max_delivery_time_param:
            queryset = queryset.annotate(max_delivery=Max('details__delivery_time_in_days')).filter(max_delivery__lte=max_delivery_time_param)
        
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return OfferCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OfferUpdateSerializer
        elif self.action == 'retrieve':
            return OfferDetailSerializer
        return OfferListSerializer