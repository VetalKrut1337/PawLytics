from django.urls import path
from hotels.views import (
    CreateHotelView, RoomVisitsPerYearView, RoomProfitPerYearView,
    RoomExpensesPerYearView, VisitsBySpeciesView, AverageFoodBySpeciesView,
    ComplexAnalyticsView
)

urlpatterns = [
    path('create-hotel/', CreateHotelView.as_view(), name='create-hotel'),
    path('room-visits/', RoomVisitsPerYearView.as_view(), name='room-visits'),
    path('room-profit/', RoomProfitPerYearView.as_view(), name='room-profit'),
    path('room-expenses/', RoomExpensesPerYearView.as_view(), name='room-expenses'),
    path('visits-by-species/', VisitsBySpeciesView.as_view(), name='visits-by-species'),
    path('avg-food-by-species/', AverageFoodBySpeciesView.as_view(), name='avg-food-by-species'),
    path('complex-analytics/', ComplexAnalyticsView.as_view(), name='complex-analytics'),
]
