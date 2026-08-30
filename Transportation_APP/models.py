from django.conf import settings
from django.db import models

CITY_CHOICES = [
    ("Lviv", "Lviv"),
    ("Zolochiv", "Zolochiv"),
    ("Ternopil", "Ternopil"),
    ("Kraków", "Kraków"),
    ("Wrocław", "Wrocław"),
    ("Zielona Góra", "Zielona Góra"),
    ("Świebodzin", "Świebodzin"),
    ("Słubice", "Słubice"),
    ("Kostrzyn nad Odrą", "Kostrzyn nad Odrą"),
    ("Berlin", "Berlin"),
]


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    from_city = models.CharField(max_length=60, choices=CITY_CHOICES)
    to_city = models.CharField(max_length=60, choices=CITY_CHOICES)
    departure_date = models.DateField()
    bus_number = models.PositiveIntegerField(default=1)
    seat_number = models.PositiveIntegerField(default=1)
    baggage = models.BooleanField(default=False)
    comments = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_date", "bus_number", "seat_number"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.from_city} → {self.to_city}"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    from_city = models.CharField(max_length=60, choices=CITY_CHOICES)
    to_city = models.CharField(max_length=60, choices=CITY_CHOICES)
    departure_date = models.DateField()
    bus_number = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    comments = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_date", "bus_number"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.from_city} → {self.to_city} ({self.weight_kg} кг)"

