# views.py
from django.db.models.functions import TruncMonth
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from collections import defaultdict
from calendar import month_abbr
from django.db.models import Sum, Avg, Count
from decimal import Decimal

from hotels.serializers import HotelCreateSerializer
from server.models import (
    UserProfile, Hotel, Room, Booking, Pet, FeedingLog, RoomExpense
)


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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Рік, за який потрібна статистика (наприклад 2024). Якщо не вказати — використається поточний.",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        try:
            year = int(request.query_params.get("year", datetime.now().year))
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year)

        result = defaultdict(lambda: defaultdict(int))
        for booking in bookings:
            room_label = f"Room_{booking.room.number}"
            month = month_abbr[booking.start_date.month]
            result[room_label][month] += 1

        return Response({k: dict(v) for k, v in result.items()})


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from decimal import Decimal

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from decimal import Decimal


class RoomProfitPerYearView(APIView):
    """Считает прибыль по комнатам за год (по месяцам)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Рік, за який потрібна статистика (наприклад 2024). Якщо не вказати — використається поточний.",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        try:
            year = int(request.query_params.get("year", datetime.now().year))
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year)

        result = defaultdict(lambda: defaultdict(Decimal))
        for booking in bookings:
            room_label = f"Room_{booking.room.number}"
            month = month_abbr[booking.start_date.month]

            # Если в модели Booking есть price — используем его
            if hasattr(booking, "price"):
                price = booking.price
            else:
                # Считаем как цена комнаты * кол-во дней
                days = (booking.end_date - booking.start_date).days
                price = booking.room.price_per_night * days

            result[room_label][month] += Decimal(price)

        # Приводим к обычным dict, чтобы JSON сериализатор не ругался
        final_result = {room: {m: float(v) for m, v in months.items()} for room, months in result.items()}

        return Response(final_result)


class RoomExpensesPerYearView(APIView):
    """Считает расходы по комнатам за год (по месяцам)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        year = datetime.now().year
        rooms = Room.objects.filter(hotel=hotel)
        expenses = RoomExpense.objects.filter(room__in=rooms, date__year=year)

        result = defaultdict(lambda: defaultdict(Decimal))
        for exp in expenses:
            room_label = f"Room_{exp.room.number}"
            month = month_abbr[exp.date.month]
            result[room_label][month] += exp.amount

        return Response(result)


class VisitsBySpeciesView(APIView):
    """Количество посещений в зависимости от вида животного"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        year = datetime.now().year
        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year).select_related("pet")

        result = defaultdict(int)
        for booking in bookings:
            species = booking.pet.species
            result[species] += 1

        return Response(result)


class AverageFoodBySpeciesView(APIView):
    """Среднее количество корма по видам"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        pets = Pet.objects.filter(
            booking__room__hotel=hotel
        ).distinct()
        feedings = FeedingLog.objects.filter(pet__in=pets)

        result = defaultdict(Decimal)
        species_count = defaultdict(int)

        for feeding in feedings:
            species = feeding.pet.species
            result[species] += feeding.food_amount
            species_count[species] += 1

        avg_result = {sp: (result[sp] / species_count[sp]) for sp in result}
        return Response(avg_result)


class ComplexAnalyticsView(APIView):
    """Сложная аналитика: прибыль минус расходы с учётом количества посещений и среднего потребления корма"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        year = datetime.now().year
        rooms = Room.objects.filter(hotel=hotel)

        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year)
        expenses = RoomExpense.objects.filter(room__in=rooms, date__year=year)
        feedings = FeedingLog.objects.filter(pet__hotel=hotel, date__year=year)

        data = {}
        for room in rooms:
            profit = sum(b.total_price for b in bookings if b.room == room)
            cost = sum(e.amount for e in expenses if e.room == room)
            visits = sum(1 for b in bookings if b.room == room)
            avg_food = feedings.filter(pet__room=room).aggregate(avg=Avg("food_amount"))["avg"] or 0
            net_profit = profit - cost - (avg_food * visits * Decimal("0.01"))  # условно корм стоит 0.01 за грамм

            data[f"Room_{room.number}"] = {
                "profit": profit,
                "expenses": cost,
                "visits": visits,
                "avg_food": avg_food,
                "net_profit": net_profit
            }

        return Response(data)
