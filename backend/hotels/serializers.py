from pawlytics.models import Hotel
from rest_framework import serializers


class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'address']