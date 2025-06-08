from rest_framework import generics
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class MyHotelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hotel = request.user.userprofile.hotel
        return Response({
            "hotel": hotel.name if hotel else None
        })