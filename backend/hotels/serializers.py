from server.models import Hotel, Room, Booking, PetType, Breed, FeedingLog, RoomExpense, Pet, Payment
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

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'number', 'capacity']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'pet', 'room', 'start_date', 'end_date', 'price']


class PetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetType
        fields = ['id', 'name']


class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = ['id', 'name', 'pet_type']


class FeedingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedingLog
        fields = ['id', 'pet', 'date', 'food_amount']


class RoomExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomExpense
        fields = ['id', 'room', 'date', 'amount', 'description']