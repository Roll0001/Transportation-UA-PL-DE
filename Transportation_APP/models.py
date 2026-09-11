from datetime import date, timedelta

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


class BusGroup(models.Model):
    KIND_CHOICES = [
        ("outbound", "Рейси в напрямку"),
        ("return", "Рейси повернення"),
    ]

    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="outbound")

    class Meta:
        ordering = ["kind", "name"]

    def __str__(self):
        return self.name


class Bus(models.Model):
    DIRECTION_CHOICES = [
        ("outbound", "Рейси в напрямку"),
        ("return", "Рейси повернення"),
    ]

    number = models.PositiveIntegerField(default=1)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default="outbound")
    departure_date = models.DateField()
    departure_time = models.TimeField(default="06:00")
    return_date = models.DateField()
    return_time = models.TimeField(default="06:00")
    note = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["direction", "number"]

    def __str__(self):
        return f"Автобус {self.number} — {self.get_direction_display()}"


def create_default_bus_records():
    from .forms import get_bus_direction_dates

    default_buses = []
    for bus_number in [1, 2]:
        outbound_departure, outbound_return = get_bus_direction_dates(bus_number, is_return_trip=False)
        return_departure, return_return = get_bus_direction_dates(bus_number, is_return_trip=True)

        default_buses.extend([
            {
                "number": bus_number,
                "direction": "outbound",
                "departure_date": outbound_departure,
                "return_date": outbound_return,
                "note": "Автобус у напрямку до польського маршруту.",
            },
            {
                "number": bus_number,
                "direction": "return",
                "departure_date": return_departure,
                "return_date": return_return,
                "note": "Автобус повернення назад.",
            },
        ])

    created_count = 0
    for bus_data in default_buses:
        created, _ = Bus.objects.get_or_create(
            number=bus_data["number"],
            direction=bus_data["direction"],
            defaults={
                "departure_date": bus_data["departure_date"],
                "return_date": bus_data["return_date"],
                "note": bus_data["note"],
            },
        )
        if created:
            created_count += 1

    return created_count


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    from_city = models.CharField(max_length=60, choices=CITY_CHOICES)
    to_city = models.CharField(max_length=60, choices=CITY_CHOICES)
    pickup_location = models.CharField(max_length=255, default="")
    dropoff_location = models.CharField(max_length=255, default="")
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
    pickup_location = models.CharField(max_length=255, default="")
    dropoff_location = models.CharField(max_length=255, default="")
    departure_date = models.DateField()
    bus_number = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    comments = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_date", "bus_number"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.from_city} → {self.to_city} ({self.weight_kg} кг)"

