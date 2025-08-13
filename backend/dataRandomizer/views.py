import random
from datetime import timedelta, date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from faker import Faker

from server.models import (
    Room, Staff, Service, ServiceUsage, Inventory, Purchase, PurchaseItem,
    PetType, PetOwner, Pet, Booking, Payment, UserProfile
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

        return Response({"status": "OK", "message": "Дані успішно згенеровані за 2 роки"})
