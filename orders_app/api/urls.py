from django.urls import path
from orders_app.views import OrderViewSet, OrderCountView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls + [
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count')
]


# urlpatterns = [
#     path('orders/', ListCreateOrderView.as_view(), name='order-create'),
#     path('orders/<int:pk>/', UpdateDeleteOrderView.as_view(), name='order-update-delete'),
# ]