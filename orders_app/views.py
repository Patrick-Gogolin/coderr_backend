from django.shortcuts import render
from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]