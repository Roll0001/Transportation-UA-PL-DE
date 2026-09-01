from datetime import date, timedelta

from django import forms

from .models import Booking, Post, CITY_CHOICES


def get_bus_direction_dates(bus_number, is_return_trip=False):
    today = date.today()

    if is_return_trip:
        departure_weekdays = {
            1: 2,
            2: 5,
        }
    else:
        departure_weekdays = {
            1: 1,
            2: 4,
        }

    departure_weekday = departure_weekdays.get(bus_number)
    if departure_weekday is None:
        return today, today

    days_until_departure = (departure_weekday - today.weekday()) % 7
    if days_until_departure == 0:
        days_until_departure = 7
    departure_date = today + timedelta(days=days_until_departure)

    return_date = departure_date + timedelta(days=2)
    return departure_date, return_date


def get_bus_dates(bus_number):
    return get_bus_direction_dates(bus_number, is_return_trip=False)


def get_bus_departure_date(bus_number):
    return get_bus_dates(bus_number)[0]


class BookingForm(forms.ModelForm):
    bus_number = forms.IntegerField(required=False, widget=forms.HiddenInput())
    first_name = forms.CharField(label="Ім'я", max_length=60)
    last_name = forms.CharField(label="Прізвище", max_length=60)
    phone = forms.CharField(label="Телефон", max_length=20)
    seat_number = forms.IntegerField(min_value=1, max_value=24, label="Номер місця")
    from_city = forms.ChoiceField(choices=CITY_CHOICES, label="Звідки")
    to_city = forms.ChoiceField(choices=CITY_CHOICES, label="Куди")
    departure_date = forms.DateField(required=False, widget=forms.HiddenInput(), label="Дата відправлення")
    baggage = forms.BooleanField(required=False, label="Багаж")
    comments = forms.CharField(required=False, label="Коментар", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get("seat_number"):
            self.fields["seat_number"].widget.attrs["value"] = self.initial["seat_number"]
        if self.initial.get("from_city"):
            self.fields["from_city"].initial = self.initial["from_city"]
        if self.initial.get("to_city"):
            self.fields["to_city"].initial = self.initial["to_city"]
        if self.initial.get("bus_number"):
            self.fields["bus_number"].initial = self.initial["bus_number"]
        if self.initial.get("departure_date"):
            self.fields["departure_date"].initial = self.initial["departure_date"]

    class Meta:
        model = Booking
        fields = [
            "first_name",
            "last_name",
            "phone",
            "from_city",
            "to_city",
            "departure_date",
            "bus_number",
            "seat_number",
            "baggage",
            "comments",
        ]
        labels = {
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "phone": "Телефон",
            "from_city": "Звідки",
            "to_city": "Куди",
            "departure_date": "Дата відправлення",
            "seat_number": "Номер місця",
            "baggage": "Багаж",
            "comments": "Коментар",
        }
        widgets = {
            "departure_date": forms.HiddenInput(),
            "comments": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_city = cleaned_data.get("from_city")
        to_city = cleaned_data.get("to_city")
        seat_number = cleaned_data.get("seat_number")
        bus_number = cleaned_data.get("bus_number") or 1
        departure_date = cleaned_data.get("departure_date")

        if from_city and to_city and from_city == to_city:
            raise forms.ValidationError("Місто відправлення та прибуття не може бути однаковим.")

        cleaned_data["bus_number"] = bus_number
        if not departure_date and bus_number:
            cleaned_data["departure_date"] = get_bus_departure_date(bus_number)
            departure_date = cleaned_data["departure_date"]

        if not departure_date:
            raise forms.ValidationError("Оберіть маршрут із доступних місць, щоб автоматично встановити дату виїзду.")

        if seat_number and departure_date and bus_number:
            existing = Booking.objects.filter(
                seat_number=seat_number,
                departure_date=departure_date,
                bus_number=bus_number,
            ).exists()
            if existing:
                raise forms.ValidationError("Це місце вже заброньоване на обрану дату в цьому автобусі.")

        return cleaned_data


class PostForm(forms.ModelForm):
    first_name = forms.CharField(label="Ім'я", max_length=60)
    last_name = forms.CharField(label="Прізвище", max_length=60)
    phone = forms.CharField(label="Телефон", max_length=20)
    from_city = forms.ChoiceField(choices=CITY_CHOICES, label="Звідки")
    to_city = forms.ChoiceField(choices=CITY_CHOICES, label="Куди")
    weight_kg = forms.DecimalField(label="Вага посилки (кг)", max_digits=5, decimal_places=2, min_value=0.01, max_value=50)
    departure_date = forms.DateField(required=False, widget=forms.HiddenInput(), label="Дата відправлення")
    bus_number = forms.IntegerField(required=False, widget=forms.HiddenInput())
    comments = forms.CharField(required=False, label="Коментар", widget=forms.Textarea(attrs={"rows": 3}))

    class Meta:
        model = Post
        fields = [
            "first_name",
            "last_name",
            "phone",
            "from_city",
            "to_city",
            "weight_kg",
            "departure_date",
            "bus_number",
            "comments",
        ]
        labels = {
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "phone": "Телефон",
            "from_city": "Звідки",
            "to_city": "Куди",
            "weight_kg": "Вага посилки (кг)",
            "comments": "Коментар",
        }
        widgets = {
            "departure_date": forms.HiddenInput(),
            "bus_number": forms.HiddenInput(),
            "comments": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_city = cleaned_data.get("from_city")
        to_city = cleaned_data.get("to_city")
        weight_kg = cleaned_data.get("weight_kg")

        if from_city and to_city and from_city == to_city:
            raise forms.ValidationError("Місто відправлення та прибуття не може бути однаковим.")

        if weight_kg and weight_kg > 50:
            raise forms.ValidationError("Максимальна вага посилки — 50 кг.")

        return cleaned_data
