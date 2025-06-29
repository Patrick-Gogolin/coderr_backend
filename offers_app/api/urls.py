from django.urls import path
from offers_app.api.views import OfferViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = router.urls