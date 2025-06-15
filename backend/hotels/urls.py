from hotels.views import CreateHotelView
from django.urls import path

urlpatterns = [
    path('create-hotel/', CreateHotelView.as_view(), name='create-hotel'),
]