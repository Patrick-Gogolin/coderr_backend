from django.shortcuts import render
from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer, OrderUpdateSerializer
from rest_framework import viewsets
from rest_framework import generics
from orders_app.api.permissions import isUserFromTypeCustomer

# Create your views here.
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [isUserFromTypeCustomer]

class UpdateOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer