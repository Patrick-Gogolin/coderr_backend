from django.urls import path
from reviews_app.api.views import ReviewViewSet, GeneralInformationView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = router.urls + [
    path('base-info/', GeneralInformationView.as_view(), name='general-information'),
]