from server.models import Hotel, Room, Booking
from rest_framework import serializers


class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'location']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'number', 'capacity']


class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer()

    class Meta:
        model = Booking
        fields = ['room', 'start_date', 'end_date']