from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from collections import defaultdict
from server.models import Booking, Room
from calendar import month_abbr

from hotels.serializers import HotelCreateSerializer
from server.models import UserProfile


class CreateHotelView(generics.CreateAPIView):
    serializer_class = HotelCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        hotel = serializer.save()
        profile = self.request.user.userprofile
        profile.hotel = hotel
        profile.save()


class RoomVisitsPerYearView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel

        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        year = datetime.now().year
        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year)

        # Структура:
        # { 'Room_201': { 'Jan': 2, 'Feb': 3, ... } }
        result = defaultdict(lambda: defaultdict(int))

        for booking in bookings:
            room_label = f"Room_{booking.room.number}"
            month = month_abbr[booking.start_date.month]
            result[room_label][month] += 1

        return Response(result)
