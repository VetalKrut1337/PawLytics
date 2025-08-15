# views.py
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from collections import defaultdict
from calendar import month_abbr
from django.db.models import Sum, Avg, Count

from hotels.serializers import HotelCreateSerializer
from server.models import (
    UserProfile, Hotel, Room, Booking, Pet, FeedingLog, RoomExpense
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from decimal import Decimal


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

        # Получаем год из query params или текущий
        year_param = request.query_params.get("year")
        try:
            year = int(year_param) if year_param else datetime.now().year
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        rooms = Room.objects.filter(hotel=hotel)
        expenses = RoomExpense.objects.filter(room__in=rooms, date__year=year)

        result = defaultdict(lambda: defaultdict(Decimal))
        for exp in expenses:
            room_label = f"Room_{exp.room.number}"
            month = month_abbr[exp.date.month]
            result[room_label][month] += exp.amount

        # Преобразуем Decimal в float для корректного JSON
        final_result = {room: {m: float(v) for m, v in months.items()} for room, months in result.items()}

        return Response(final_result)


class VisitsBySpeciesView(APIView):
    """Количество посещений в зависимости от вида животного"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Рік, за який потрібно отримати статистику (наприклад, 2024). Якщо не вказати — використається поточний.",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request):
        # Получаем пользователя и его отель
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        # Получаем год из query params или берем текущий
        year = request.query_params.get("year")
        try:
            year = int(year) if year else datetime.now().year
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        # Получаем комнаты и бронирования за выбранный год
        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(
            room__in=rooms,
            start_date__year=year
        ).select_related("pet__pet_type")

        # Считаем количество посещений по виду
        result = defaultdict(int)
        for booking in bookings:
            species = booking.pet.pet_type.name
            result[species] += 1

        return Response(result)


class AverageFoodBySpeciesView(APIView):
    """Среднее количество корма по видам"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Рік, за який потрібно отримати статистику (за датою кормлень)",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        # Получаем год из query params
        year_param = request.query_params.get("year")
        try:
            year = int(year_param) if year_param else None
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        # Получаем все питомцы, у которых были бронирования в этом отеле
        pets = Pet.objects.filter(booking__room__hotel=hotel).distinct()

        # Фильтруем кормления по питомцам и году
        feedings = FeedingLog.objects.filter(pet__in=pets)
        if year:
            feedings = feedings.filter(date__year=year)

        # Суммируем количество корма и считаем количество записей для среднего
        total_food = defaultdict(Decimal)
        count_food = defaultdict(int)

        for feeding in feedings.select_related("pet__pet_type"):
            species_name = feeding.pet.pet_type.name
            total_food[species_name] += feeding.food_amount
            count_food[species_name] += 1

        # Вычисляем среднее
        avg_result = {species: float(total_food[species] / count_food[species])
                      for species in total_food if count_food[species] > 0}

        return Response(avg_result)


class ComplexAnalyticsView(APIView):
    """Сложная аналитика: прибыль минус расходы с учётом количества посещений и среднего потребления корма"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Рік для статистики",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        year_param = request.query_params.get("year")
        try:
            year = int(year_param) if year_param else datetime.now().year
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year)
        expenses = RoomExpense.objects.filter(room__in=rooms, date__year=year)

        data = {}

        for room in rooms:
            room_bookings = bookings.filter(room=room)
            profit = sum(b.price for b in room_bookings)
            cost = sum(e.amount for e in expenses.filter(room=room))
            visits = room_bookings.count()

            # Получаем всех питомцев, которые бронировали эту комнату
            pets_in_room = Pet.objects.filter(booking__in=room_bookings).distinct()
            feedings_in_room = FeedingLog.objects.filter(pet__in=pets_in_room, date__year=year)
            avg_food = feedings_in_room.aggregate(avg=Avg("food_amount"))["avg"] or 0

            net_profit = profit - cost - (avg_food * visits * Decimal("0.01"))

            data[f"Room_{room.number}"] = {
                "profit": profit,
                "expenses": cost,
                "visits": visits,
                "avg_food": float(avg_food),
                "net_profit": float(net_profit)
            }

        return Response(data)


class CombinedAnalyticsView(APIView):
    """Универсальная аналитика: можно выбрать несколько метрик сразу"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Рік для статистики (наприклад 2024)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'metrics',
                openapi.IN_QUERY,
                description="Список метрик через запятую. Возможные значения: room_visits, room_profit, room_expenses, visits_by_species, avg_food, complex",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel
        if not hotel:
            return Response({"error": "Користувач не прив'язаний до готелю."}, status=400)

        # --- год ---
        year_param = request.query_params.get("year")
        try:
            year = int(year_param) if year_param else datetime.now().year
        except ValueError:
            return Response({"error": "Невірний формат року."}, status=400)

        # --- выбранные метрики ---
        metrics_param = request.query_params.get("metrics")
        if not metrics_param:
            return Response({"error": "Не вказані метрики"}, status=400)
        requested_metrics = [m.strip() for m in metrics_param.split(",")]

        # --- подготовка данных ---
        rooms = Room.objects.filter(hotel=hotel)
        bookings = Booking.objects.filter(room__in=rooms, start_date__year=year)
        expenses = RoomExpense.objects.filter(room__in=rooms, date__year=year)

        result = {}

        # --- Room Visits ---
        if "room_visits" in requested_metrics:
            room_visits = defaultdict(lambda: defaultdict(int))
            for b in bookings:
                room_label = f"Room_{b.room.number}"
                month = month_abbr[b.start_date.month]
                room_visits[room_label][month] += 1
            result["room_visits"] = {k: dict(v) for k, v in room_visits.items()}

        # --- Room Profit ---
        if "room_profit" in requested_metrics:
            room_profit = defaultdict(lambda: defaultdict(Decimal))
            for b in bookings:
                room_label = f"Room_{b.room.number}"
                month = month_abbr[b.start_date.month]
                room_profit[room_label][month] += Decimal(b.price)
            result["room_profit"] = {k: {m: float(v) for m, v in months.items()} for k, months in room_profit.items()}

        # --- Room Expenses ---
        if "room_expenses" in requested_metrics:
            room_exp = defaultdict(lambda: defaultdict(Decimal))
            for e in expenses:
                room_label = f"Room_{e.room.number}"
                month = month_abbr[e.date.month]
                room_exp[room_label][month] += e.amount
            result["room_expenses"] = {k: {m: float(v) for m, v in months.items()} for k, months in room_exp.items()}

        # --- Visits by Species ---
        if "visits_by_species" in requested_metrics:
            species_count = defaultdict(int)
            for b in bookings.select_related("pet__pet_type"):
                species_name = b.pet.pet_type.name
                species_count[species_name] += 1
            result["visits_by_species"] = dict(species_count)

        # --- Average Food ---
        if "avg_food" in requested_metrics:
            pets = Pet.objects.filter(booking__room__hotel=hotel).distinct()
            feedings = FeedingLog.objects.filter(pet__in=pets, date__year=year)
            total_food = defaultdict(Decimal)
            count_food = defaultdict(int)
            for f in feedings.select_related("pet__pet_type"):
                species_name = f.pet.pet_type.name
                total_food[species_name] += f.food_amount
                count_food[species_name] += 1
            avg_food = {sp: float(total_food[sp]/count_food[sp]) for sp in total_food if count_food[sp]>0}
            result["avg_food"] = avg_food

        # --- Complex Analytics ---
        if "complex" in requested_metrics:
            complex_data = {}
            for room in rooms:
                room_bookings = bookings.filter(room=room)
                profit = sum(b.price for b in room_bookings)
                cost = sum(e.amount for e in expenses.filter(room=room))
                visits = room_bookings.count()
                pets_in_room = Pet.objects.filter(booking__in=room_bookings).distinct()
                feedings_in_room = FeedingLog.objects.filter(pet__in=pets_in_room, date__year=year)
                avg_food = feedings_in_room.aggregate(avg=Avg("food_amount"))["avg"] or 0
                net_profit = profit - cost - (avg_food * visits * Decimal("0.01"))
                complex_data[f"Room_{room.number}"] = {
                    "profit": profit,
                    "expenses": cost,
                    "visits": visits,
                    "avg_food": float(avg_food),
                    "net_profit": float(net_profit)
                }
            result["complex"] = complex_data

        return Response(result)