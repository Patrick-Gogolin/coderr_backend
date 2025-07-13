from django.shortcuts import get_object_or_404
from orders_app.models import Order
from user_auth_app.models import User
from orders_app.api.serializers import OrderSerializer, OrderUpdateSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status, permissions
from rest_framework.response import Response
from orders_app.api.permissions import isUserFromTypeCustomer

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [isUserFromTypeCustomer]

    def get_serializer_class(self):
        if self.action in ['create', 'list']:
            return OrderSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "Retrieving a single order is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class OrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)

        if getattr(business_user.userprofile, 'type', None) != 'business':
            return Response({'detail': 'User is not a business user'}, status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter(business_user=business_user, status='in_progress').count()

        return Response({'order_count': count}, status=status.HTTP_200_OK)

class CompletedOrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)

        if getattr(business_user.userprofile, 'type', None) != 'business':
            return Response({'detail': 'User is not a business user'}, status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter(business_user=business_user, status='completed').count()

        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)
