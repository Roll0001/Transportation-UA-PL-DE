from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum

from .forms import BookingForm, PostForm, get_bus_departure_date
from .models import Booking, Post


def is_admin_user(user):
    return (
        user.is_authenticated and 
        (user.is_staff or user.is_superuser or user.groups.filter(name='admin').exists())
    )


def get_available_bus_for_post(weight_kg):
    """
    Вибирає найвільніший автобус для посилки (максимум 30 кг на автобус).
    Повертає номер автобуса і дату вилету.
    """
    MAX_WEIGHT_PER_BUS = 30
    
    for bus_number in [1, 2]:
        departure_date = get_bus_departure_date(bus_number)
        
        total_weight = Post.objects.filter(
            bus_number=bus_number,
            departure_date=departure_date
        ).aggregate(total=Sum('weight_kg'))['total'] or 0
        
        if float(total_weight) + float(weight_kg) <= MAX_WEIGHT_PER_BUS:
            return bus_number, departure_date
    
    # Якщо обидва автобуси перевантажені, повертаємо меньш навантажений
    bus_weights = {}
    for bus_number in [1, 2]:
        departure_date = get_bus_departure_date(bus_number)
        total_weight = Post.objects.filter(
            bus_number=bus_number,
            departure_date=departure_date
        ).aggregate(total=Sum('weight_kg'))['total'] or 0
        bus_weights[bus_number] = (float(total_weight), departure_date)
    
    bus_number, (_, departure_date) = min(bus_weights.items(), key=lambda x: x[1][0])
    return bus_number, departure_date


def home_page(request):
    if not request.user.is_authenticated:
        return redirect('register')
    route_stops = [
        "Lviv",
        "Zolochiv",
        "Ternopil",
        "Kraków",
        "Wrocław",
        "Zielona Góra",
        "Świebodzin",
        "Słubice",
        "Kostrzyn nad Odrą",
        "Berlin",
    ]
    return render(request, "home.html", {"route_stops": route_stops})


def available_spots_page(request):
    buses = []
    for bus_number in [1, 2]:
        occupied = sorted(set(
            Booking.objects.filter(bus_number=bus_number).values_list("seat_number", flat=True)
        ))
        buses.append({
            "number": bus_number,
            "seats": list(range(1, 9)),
            "occupied": [seat for seat in range(1, 9) if seat in occupied],
            "schedule": "Регулярний маршрут: виїзд у понеділок вранці, повернення у середу." if bus_number == 1 else "Регулярний маршрут: виїзд у п'ятницю, повернення в суботу.",
            "note": "Маршрут виконується регулярно по розкладу.",
        })
    return render(request, "availablespots.html", {"buses": buses})


@login_required(login_url="/auth/login/")
def booking_page(request):
    initial = {
        "from_city": "Lviv",
        "to_city": "Berlin",
    }

    selected_seat = request.GET.get("seat")
    selected_bus = request.GET.get("bus")
    if selected_seat:
        initial["seat_number"] = selected_seat
    if selected_bus:
        initial["bus_number"] = int(selected_bus)
        initial["departure_date"] = get_bus_departure_date(int(selected_bus))

    form = BookingForm(initial=initial)
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.bus_number = form.cleaned_data.get("bus_number") or int(request.GET.get("bus", 1))
            booking.departure_date = get_bus_departure_date(booking.bus_number)
            booking.save()
            messages.success(request, "Бронювання успішно створено.")
            return redirect("my_bookings")
    return render(request, "booking.html", {"form": form})


@login_required(login_url="/auth/login/")
def my_bookings_page(request):
    bookings = Booking.objects.filter(user=request.user).order_by("departure_date", "seat_number")
    posts = Post.objects.filter(user=request.user).order_by("departure_date", "bus_number")
    return render(request, "mybooking.html", {"bookings": bookings, "posts": posts})


@login_required(login_url="/auth/login/")
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    messages.success(request, "Бронювання скасовано.")
    return redirect("my_bookings")


@login_required(login_url="/auth/login/")
def cancel_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    messages.success(request, "Передачу скасовано.")
    return redirect("my_bookings")


@login_required(login_url="/auth/login/")
def post_page(request):
    form = PostForm(initial={
        "from_city": "Lviv",
        "to_city": "Berlin",
    })
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            weight_kg = form.cleaned_data.get("weight_kg")
            bus_number, departure_date = get_available_bus_for_post(weight_kg)
            
            post = form.save(commit=False)
            post.user = request.user
            post.bus_number = bus_number
            post.departure_date = departure_date
            post.save()
            messages.success(request, f"Передача/посилка успішно оформлена на автобус {bus_number}.")
            return redirect("my_bookings")
    return render(request, "post.html", {"form": form})


@login_required(login_url="/auth/login/")
def secret_page(request):
    if not is_admin_user(request.user):
        return redirect('home')
    bookings = Booking.objects.all().order_by("departure_date", "seat_number")
    posts = Post.objects.all().order_by("departure_date", "bus_number")
    return render(request, "secret_page.html", {"bookings": bookings, "posts": posts})
