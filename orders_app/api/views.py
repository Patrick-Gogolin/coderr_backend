from django.shortcuts import get_object_or_404
from orders_app.models import Order
from user_auth_app.models import User
from orders_app.api.serializers import OrderSerializer, OrderUpdateSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status, permissions
from rest_framework.response import Response
from orders_app.api.permissions import isUserFromTypeCustomer
from django.db.models import Q


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing `Order` objects.

    Permissions:
    - Only users with the `customer` user profile type are allowed.

    Behaviors:
    - `list`: Returns all orders where the user is either the customer or the business.
    - `create`: Creates a new order for a customer.
    - `update` / `partial_update`: Updates an existing order.
    - `retrieve`: Not allowed. Returns 405 Method Not Allowed.

    Queryset:
    - Filters orders where the current user is either the `customer_user` or `business_user`.

    Serializers:
    - `OrderSerializer`: Used for create and list actions.
    - `OrderUpdateSerializer`: Used for update actions.
    """
    permission_classes = [isUserFromTypeCustomer]

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))
        return Order.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'list']:
            return OrderSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "Retrieving a single order is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class OrderCountView(APIView):
    """
    API view to get the count of `in_progress` orders for a given business user.

    Permissions:
    - Requires the user to be authenticated.

    Path Parameters:
    - `business_user_id`: ID of the business user.

    Returns:
    - HTTP 200 with the order count if the user is a valid business user.
    - HTTP 404 if the user does not exist or is not a business user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)

        if getattr(business_user.userprofile, 'type', None) != 'business':
            return Response({'detail': 'User is not a business user'}, status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter(business_user=business_user, status='in_progress').count()

        return Response({'order_count': count}, status=status.HTTP_200_OK)

class CompletedOrderCountView(APIView):
    """
    API view to get the count of `completed` orders for a given business user.

    Permissions:
    - Requires the user to be authenticated.

    Path Parameters:
    - `business_user_id`: ID of the business user.

    Returns:
    - HTTP 200 with the completed order count if the user is a valid business user.
    - HTTP 404 if the user does not exist or is not a business user.
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)

        if getattr(business_user.userprofile, 'type', None) != 'business':
            return Response({'detail': 'User is not a business user'}, status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter(business_user=business_user, status='completed').count()

        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)