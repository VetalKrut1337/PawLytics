import random
from datetime import timedelta, date, datetime
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
        for i in range(5):
            room = Room.objects.create(
                hotel=hotel,
                number=f"{200 + i}",
                capacity=random.randint(1, 3)
            )
            rooms.append(room)

        # --- Staff ---
        staff_list = []
        for _ in range(3):
            staff = Staff.objects.create(
                hotel=hotel,
                name=fake.name(),
                role=random.choice(['Caretaker', 'Cleaner', 'Trainer']),
                phone=fake.phone_number()
            )
            staff_list.append(staff)

        # --- Services ---
        services = []
        for name in ['Grooming', 'Training', 'Vet Check']:
            service = Service.objects.create(
                name=name,
                description=fake.sentence(),
                price=random.randint(50, 200)
            )
            services.append(service)

        # --- Service Usage ---
        for _ in range(10):
            ServiceUsage.objects.create(
                service=random.choice(services),
                staff=random.choice(staff_list),
                date=fake.date_this_year(),
                amount=random.randint(1, 5)
            )

        # --- Inventory ---
        inventory_items = []
        for i in range(3):
            inv = Inventory.objects.create(
                hotel=hotel,
                name=fake.word(),
                category=random.choice(['Food', 'Toys', 'Medicine']),
                quantity=random.randint(10, 50),
                unit='pcs',
                min_required=5
            )
            inventory_items.append(inv)

        # --- Purchases ---
        for _ in range(3):
            purchase = Purchase.objects.create(
                hotel=hotel,
                date=fake.date_this_year(),
                supplier=fake.company(),
                total_cost=0  # Updated below
            )
            total = 0
            for _ in range(random.randint(1, 3)):
                item = random.choice(inventory_items)
                qty = random.randint(1, 10)
                price = random.randint(5, 20)
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

        # --- Pet Owners ---
        owners = []
        for _ in range(3):
            owner = PetOwner.objects.create(
                name=fake.name(),
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address()
            )
            owners.append(owner)

        # --- Pets + Bookings + Payments ---
        for _ in range(5):
            pet = Pet.objects.create(
                pet_type=random.choice([dog, cat]),
                pet_owner=random.choice(owners),
                birth_date=fake.date_of_birth(minimum_age=1, maximum_age=12),
                weight=random.uniform(2.0, 20.0),
                medical_notes=fake.sentence()
            )

            room = random.choice(rooms)
            start_date = fake.date_between(start_date='-6M', end_date='today')
            end_date = start_date + timedelta(days=random.randint(1, 7))

            booking = Booking.objects.create(
                pet=pet,
                room=room,
                start_date=start_date,
                end_date=end_date,
                price=random.randint(100, 500)
            )

            Payment.objects.create(
                booking=booking,
                amount=booking.price,
                date=end_date,
                payment_method=random.choice(['Cash', 'Card'])
            )

        return Response({"status": "OK", "message": "Дані успішно згенеровані"})
