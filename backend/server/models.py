from django.contrib.auth.models import User
from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    number = models.CharField(max_length=50)
    capacity = models.IntegerField()


class Staff(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)


class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()


class ServiceUsage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    date = models.DateField()
    amount = models.IntegerField()


class Inventory(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    min_required = models.IntegerField()


class Purchase(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    date = models.DateField()
    supplier = models.CharField(max_length=255)
    total_cost = models.IntegerField()


class PurchaseItem(models.Model):
    item = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.IntegerField()


class PetType(models.Model):
    name = models.CharField(max_length=255)


class PetOwner(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.TextField()


class Pet(models.Model):
    pet_type = models.ForeignKey(PetType, on_delete=models.PROTECT)
    breed = models.ForeignKey('Breed', null=True, blank=True, on_delete=models.SET_NULL)
    pet_owner = models.ForeignKey(PetOwner, on_delete=models.PROTECT)
    birth_date = models.DateField()
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    medical_notes = models.TextField()


class Breed(models.Model):
    pet_type = models.ForeignKey(PetType, on_delete=models.PROTECT, related_name="breeds")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.pet_type.name})"


class FeedingLog(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.PROTECT, related_name="feedings")
    date = models.DateTimeField()
    food_amount = models.DecimalField(max_digits=6, decimal_places=2)  # граммы

    def __str__(self):
        return f"{self.pet} — {self.food_amount}g on {self.date}"


class RoomExpense(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="expenses")
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.room.number} — {self.amount} on {self.date}"


class Booking(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.IntegerField()


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT)
    amount = models.IntegerField()
    date = models.DateField()
    payment_method = models.CharField(max_length=100)


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.PROTECT)
    hotel = models.ForeignKey(Hotel, null=True, blank=True, on_delete=models.PROTECT)
    role = models.CharField(max_length=50, default='staff')

    def __str__(self):
        return f"{self.user.username} — {self.role}"
