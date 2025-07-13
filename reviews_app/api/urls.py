from django.urls import path
from reviews_app.api.views import CreateReviewView


urlpatterns = [
    path('reviews/', CreateReviewView.as_view(), name='create_review')
]