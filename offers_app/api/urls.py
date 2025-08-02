from django.urls import path
from rest_framework.routers import DefaultRouter
from offers_app.api.views import OfferViewSet, OfferDetails


router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = router.urls + [
    path('offerdetails/<int:pk>/', OfferDetails.as_view(), name='offer-details')
]