from django.urls import path
from .views import GenerateRandomDataView, ClearRandomDataView

urlpatterns = [
    path('generate-data/', GenerateRandomDataView.as_view(), name='generate-data'),
    path('clear-random-data/', ClearRandomDataView.as_view(), name='clear-random-data'),
]