from django.urls import path
from orders_app.views import OrderCreateView

#router = DefaultRouter()
#router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('orders/', OrderCreateView.as_view(), name='order-create')
]