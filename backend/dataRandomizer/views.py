import random
from datetime import timedelta, date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from faker import Faker

from server.models import (
    Room, Staff, Service, ServiceUsage, Inventory, Purchase, PurchaseItem,
    PetType, PetOwner, Pet, Booking, Payment, UserProfile, Breed, FeedingLog, RoomExpense
)

fake = Faker()

class GenerateRandomDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        hotel = user_profile.hotel

        if not hotel:
            return Response({"error": "User is not associated with any hotel."}, status=400)

        # --- Rooms ---
        rooms = []
        for i in range(10):  # більше кімнат
            room = Room.objects.create(
                hotel=hotel,
                number=f"{200 + i}",
                capacity=random.randint(1, 4)
            )
            rooms.append(room)

        # --- Staff ---
        staff_list = []
        for _ in range(8):  # більше персоналу
            staff = Staff.objects.create(
                hotel=hotel,
                name=fake.name(),
                role=random.choice(['Caretaker', 'Cleaner', 'Trainer', 'Vet']),
                phone=fake.phone_number()
            )
            staff_list.append(staff)

        # --- Services ---
        service_names = ['Grooming', 'Training', 'Vet Check', 'Walking', 'Feeding']
        services = []
        for name in service_names:
            service = Service.objects.create(
                name=name,
                description=fake.sentence(),
                price=random.randint(50, 300)
            )
            services.append(service)

        # --- Service Usage (за 2 роки) ---
        for _ in range(200):
            ServiceUsage.objects.create(
                service=random.choice(services),
                staff=random.choice(staff_list),
                date=fake.date_between(start_date='-2y', end_date='today'),
                amount=random.randint(1, 5)
            )

        # --- Inventory ---
        inventory_items = []
        for _ in range(10):
            inv = Inventory.objects.create(
                hotel=hotel,
                name=fake.word(),
                category=random.choice(['Food', 'Toys', 'Medicine', 'Bedding']),
                quantity=random.randint(20, 100),
                unit='pcs',
                min_required=random.randint(5, 15)
            )
            inventory_items.append(inv)

        # --- Purchases (за 2 роки) ---
        for _ in range(50):
            purchase_date = fake.date_between(start_date='-2y', end_date='today')
            purchase = Purchase.objects.create(
                hotel=hotel,
                date=purchase_date,
                supplier=fake.company(),
                total_cost=0
            )
            total = 0
            for _ in range(random.randint(1, 5)):
                item = random.choice(inventory_items)
                qty = random.randint(1, 20)
                price = random.randint(5, 50)
                PurchaseItem.objects.create(
                    item=item,
                    purchase=purchase,
                    quantity=qty,
                    unit_price=price
                )
                total += qty * price
            purchase.total_cost = total
            purchase.save()

        # --- Pet Types ---
        dog = PetType.objects.get_or_create(name='Dog')[0]
        cat = PetType.objects.get_or_create(name='Cat')[0]
        rabbit = PetType.objects.get_or_create(name='Rabbit')[0]

        # --- Pet Owners ---
        owners = []
        for _ in range(20):
            owner = PetOwner.objects.create(
                name=fake.name(),
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address()
            )
            owners.append(owner)

        # --- Pets + Bookings + Payments (за 2 роки) ---
        for _ in range(100):
            pet = Pet.objects.create(
                pet_type=random.choice([dog, cat, rabbit]),
                pet_owner=random.choice(owners),
                birth_date=fake.date_of_birth(minimum_age=1, maximum_age=12),
                weight=round(random.uniform(1.0, 40.0), 1),
                medical_notes=fake.sentence()
            )

            # Кілька бронювань за різні дати
            for _ in range(random.randint(1, 4)):
                start_date = fake.date_between(start_date='-2y', end_date='today')
                end_date = start_date + timedelta(days=random.randint(1, 10))

                booking = Booking.objects.create(
                    pet=pet,
                    room=random.choice(rooms),
                    start_date=start_date,
                    end_date=end_date,
                    price=random.randint(100, 1000)
                )

                Payment.objects.create(
                    booking=booking,
                    amount=booking.price,
                    date=end_date,
                    payment_method=random.choice(['Cash', 'Card', 'Online'])
                )

        # --- Breeds ---
        breeds = []
        for pet_type in [dog, cat, rabbit]:
            for _ in range(3):  # по 3 породи на тип
                breed = Breed.objects.create(
                    name=fake.word().capitalize(),
                    pet_type=pet_type
                )
                breeds.append(breed)

        # --- Feeding Logs (за 2 года) ---
        for pet in Pet.objects.all():
            for _ in range(random.randint(5, 20)):  # несколько записей кормления на питомца
                FeedingLog.objects.create(
                    pet=pet,
                    date=fake.date_time_between(start_date='-2y', end_date='now'),
                    food_amount=round(random.uniform(50, 500), 2)  # граммы
                )

        # --- Room Expenses ---
        for room in rooms:
            for _ in range(random.randint(1, 5)):
                RoomExpense.objects.create(
                    room=room,
                    date=fake.date_between(start_date='-1y', end_date='today'),
                    description=fake.sentence(),
                    amount=random.randint(100, 1000)
                )

        return Response({"status": "OK", "message": "Дані успішно згенеровані за 2 роки"})


class ClearRandomDataView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # Удаляем в правильном порядке, чтобы не было конфликтов FK
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Pet.objects.all().delete()
        PetOwner.objects.all().delete()
        Breed.objects.all().delete()
        FeedingLog.objects.all().delete()
        RoomExpense.objects.all().delete()
        ServiceUsage.objects.all().delete()
        Service.objects.all().delete()
        Staff.objects.all().delete()
        PurchaseItem.objects.all().delete()
        Purchase.objects.all().delete()
        Inventory.objects.all().delete()
        Room.objects.all().delete()
        PetType.objects.all().delete()

        return Response({"status": "OK", "message": "Всі дані згенеровані раніше — видалено"})
