from django.urls import path, include

urlpatterns = [
   path('', include('user_auth_app.api.urls')),
   path('', include('profiles_app.api.urls')),
   path('', include('offers_app.api.urls')),
   path('', include('orders_app.api.urls')),
   path('', include('reviews_app.api.urls'))
]