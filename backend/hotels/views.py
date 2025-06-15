from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from hotels.serializers import HotelCreateSerializer


class CreateHotelView(generics.CreateAPIView):
    serializer_class = HotelCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        hotel = serializer.save()
        profile = self.request.user.userprofile
        profile.hotel = hotel
        profile.save()
