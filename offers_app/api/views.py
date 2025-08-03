from rest_framework import generics
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from offers_app.models import Offer, OfferDetail

from offers_app.api.permissions import OfferPermission
from offers_app.api.serializers import OfferCreateSerializer, OfferListSerializer, OfferWithDetailsSerializer, OfferUpdateSerializer, OfferDetailSerializer


class LargeResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for Offer endpoints.

    - Limits page size to 6 results by default.
    - Supports optional `page_size` query parameter (max 6).
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6

class OfferViewSet(ModelViewSet):
    """
    ViewSet for managing offers.

    Permissions:
    - `list`: Public access (no authentication required).
    - `retrieve`: Requires authentication.
    - `create`, `update`, `partial_update`, `destroy`: Requires authentication and `OfferPermission`.

    Filtering & Ordering:
    - Supports full-text search on `title` and `description`.
    - Can be filtered by `creator_id`, `min_price`, and `max_delivery_time`.
    - Ordering fields include `updated_at` and dynamically annotated `min_price`.

    Pagination:
    - Uses `LargeResultsSetPagination` (6 items per page).

    Serializers:
    - `create`: Uses `OfferCreateSerializer`
    - `retrieve`: Uses `OfferWithDetailsSerializer`
    - `update`, `partial_update`: Uses `OfferUpdateSerializer`
    - `list`: Uses `OfferListSerializer`
    """

    queryset = Offer.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at']
    pagination_class = LargeResultsSetPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), OfferPermission()]
        return []
       
    def get_queryset(self):
        """
        Returns the filtered queryset based on query parameters:
        - `creator_id`: filters by user_id
        - `min_price`: minimum price in details
        - `max_delivery_time`: maximum delivery time in details

        Also annotates:
        - `min_price`: minimum price from related offer details
        """

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
            try:
                max_delivery_time_val = int(max_delivery_time_param)
            except:
                raise ValidationError({"max_delivery_time": "max_delivery_time has to be a number"})
            queryset = queryset.annotate(min_delivery=Min('details__delivery_time_in_days')).filter(min_delivery__lte=max_delivery_time_val)
        
        return queryset.distinct()

    def get_serializer_class(self):
        """
        Dynamically selects the appropriate serializer class based on the action.
        """

        if self.action == 'create':
            return OfferCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OfferUpdateSerializer
        elif self.action == 'retrieve':
            return OfferWithDetailsSerializer
        return OfferListSerializer

class OfferDetails(generics.RetrieveAPIView):
    """
    RetrieveAPIView for a single OfferDetail instance.

    - Requires authentication (`IsAuthenticated`).
    - Uses `OfferDetailSerializer` for representation.
    """
    
    queryset = OfferDetail.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OfferDetailSerializer