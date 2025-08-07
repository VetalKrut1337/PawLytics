from hotels.views import CreateHotelView, RoomVisitsPerYearView
from django.urls import path

urlpatterns = [
    path('create-hotel/', CreateHotelView.as_view(), name='create-hotel'),
    path('room-visits/', RoomVisitsPerYearView.as_view(), name='room-visits'),
]