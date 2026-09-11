from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('home/', views.home_page, name='home_alias'),
    path('photos/', views.photos_page, name='photos'),
    path('available-spots/', views.available_spots_page, name='available_spots'),
    path('booking/', views.booking_page, name='booking'),
    path('post/', views.post_page, name='post'),
    path('my-bookings/', views.my_bookings_page, name='my_bookings'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('post/cancel/<int:post_id>/', views.cancel_post, name='cancel_post'),
    path('secret/', views.secret_page, name='secret_page'),
]
