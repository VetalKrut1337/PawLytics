from django.urls import path
from .views import GenerateRandomDataView

urlpatterns = [
    path('generate-data/', GenerateRandomDataView.as_view(), name='generate-data'),
]