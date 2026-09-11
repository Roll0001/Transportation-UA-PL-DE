from unittest.mock import patch
from datetime import date as real_date

from django.contrib.auth import get_user_model
from django.test import TestCase

from auth_system.forms import CustomUserCreationForm
from Transportation_APP.forms import BookingForm, get_bus_dates, get_bus_direction_dates, get_next_weekday_date
from Transportation_APP.models import Booking, Bus, BusGroup


class SiteAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='pass12345')

    def test_home_page_redirects_anonymous_users_to_register(self):
        response = self.client.get('/home/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/auth/register/')

    def test_anonymous_user_redirects_to_register_from_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/auth/register/')

    def test_booking_page_redirects_anonymous_users(self):
        response = self.client.get('/booking/')
        self.assertEqual(response.status_code, 302)

    def test_available_spots_page_renders_bus_cards(self):
        response = self.client.get('/available-spots/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Автобус 1')
        self.assertContains(response, 'Автобус 2')
        self.assertNotContains(response, 'Автобус 3')
        self.assertNotContains(response, 'Автобус 4')

    def test_booking_page_accepts_preselected_seat_for_logged_user(self):
        self.client.login(username='testuser', password='pass12345')
        response = self.client.get('/booking/?seat=4')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="4"')

    def test_next_weekday_date_moves_to_next_week_when_needed(self):
        with patch('Transportation_APP.forms.date') as mocked_date:
            mocked_date.today.return_value = real_date(2026, 9, 3)
            mocked_date.side_effect = lambda *args, **kwargs: real_date(*args, **kwargs)

            self.assertEqual(get_next_weekday_date(1), real_date(2026, 9, 8))
            self.assertEqual(get_next_weekday_date(2), real_date(2026, 9, 9))
            self.assertEqual(get_next_weekday_date(4), real_date(2026, 9, 4))
            self.assertEqual(get_next_weekday_date(5), real_date(2026, 9, 5))

    def test_bus_departure_dates_follow_two_schedule_groups(self):
        bus1_first_group, _ = get_bus_dates(1)
        bus2_first_group, _ = get_bus_dates(2)
        bus1_second_group, _ = get_bus_direction_dates(1, is_return_trip=True)
        bus2_second_group, _ = get_bus_direction_dates(2, is_return_trip=True)

        self.assertEqual(bus1_first_group.weekday(), 1)
        self.assertEqual(bus2_first_group.weekday(), 4)
        self.assertEqual(bus1_second_group.weekday(), 2)
        self.assertEqual(bus2_second_group.weekday(), 5)

    def test_available_spots_page_shows_return_group_for_same_buses(self):
        response = self.client.get('/available-spots/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Автобус 1')
        self.assertContains(response, 'Автобус 2')
        self.assertContains(response, 'Рейси повернення')
        self.assertContains(response, 'Дата повернення:')

    def test_bus_database_supports_groups_and_buses(self):
        bus = Bus.objects.create(
            number=1,
            direction='outbound',
            departure_date='2026-09-08',
            return_date='2026-09-10',
            note='Test bus',
        )

        self.assertEqual(bus.direction, 'outbound')
        self.assertEqual(bus.number, 1)
        self.assertEqual(str(bus), 'Автобус 1 — Рейси в напрямку')

    def test_registration_form_requires_first_and_last_name_instead_of_email(self):
        form = CustomUserCreationForm()

        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertNotIn('email', form.fields)

    def test_post_page_loads_for_logged_user(self):
        self.client.login(username='testuser', password='pass12345')
        response = self.client.get('/post/')
        self.assertEqual(response.status_code, 200)

    def test_user_can_login_with_email(self):
        user = get_user_model().objects.create_user(
            username='email-user',
            email='user@example.com',
            password='pass12345',
        )
        response = self.client.post('/auth/login/', {
            'username': 'user@example.com',
            'password': 'pass12345',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.is_authenticated)

    def test_secret_page_requires_admin(self):
        self.client.login(username='testuser', password='pass12345')
        response = self.client.get('/secret/')
        self.assertEqual(response.status_code, 302)

    def test_admin_group_user_can_access_secret_page(self):
        admin_group = self.user.groups.create(name='admin')
        self.user.groups.add(admin_group)
        self.client.login(username='testuser', password='pass12345')
        response = self.client.get('/secret/')
        self.assertEqual(response.status_code, 200)

    def test_secret_page_filters_bookings_by_date_range(self):
        admin_group = self.user.groups.create(name='admin')
        self.user.groups.add(admin_group)
        self.client.login(username='testuser', password='pass12345')

        Booking.objects.create(
            user=self.user,
            first_name='Ann',
            last_name='Test',
            phone='123',
            from_city='Lviv',
            to_city='Berlin',
            departure_date='2026-09-10',
            seat_number=1,
            bus_number=1,
        )
        Booking.objects.create(
            user=self.user,
            first_name='Bob',
            last_name='Test',
            phone='456',
            from_city='Lviv',
            to_city='Berlin',
            departure_date='2026-09-15',
            seat_number=2,
            bus_number=2,
        )

        response = self.client.get('/secret/', {'from_date': '2026-09-09', 'to_date': '2026-09-11'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ann')
        self.assertNotContains(response, 'Bob')

    def test_seats_are_independent_between_buses(self):
        Booking.objects.create(
            user=self.user,
            first_name='Ann',
            last_name='Test',
            phone='123',
            from_city='Lviv',
            to_city='Berlin',
            departure_date='2026-09-10',
            seat_number=7,
            bus_number=1,
        )

        response = self.client.get('/available-spots/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Автобус 1')
        self.assertContains(response, 'Автобус 2')

    def test_booking_form_rejects_duplicate_seat_for_same_date(self):
        Booking.objects.create(
            user=self.user,
            first_name='Ann',
            last_name='Test',
            phone='123',
            from_city='Lviv',
            to_city='Berlin',
            departure_date='2026-09-10',
            seat_number=7,
            bus_number=1,
        )

        form = BookingForm({
            'first_name': 'Bob',
            'last_name': 'User',
            'phone': '456',
            'from_city': 'Lviv',
            'to_city': 'Berlin',
            'departure_date': '2026-09-10',
            'seat_number': 7,
            'baggage': False,
            'comments': 'test',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('Це місце вже заброньоване на обрану дату в цьому автобусі.', form.non_field_errors())

    def test_same_seat_can_be_booked_on_different_bus(self):
        Booking.objects.create(
            user=self.user,
            first_name='Ann',
            last_name='Test',
            phone='123',
            from_city='Lviv',
            to_city='Berlin',
            departure_date='2026-09-10',
            seat_number=7,
            bus_number=1,
        )

        form = BookingForm({
            'first_name': 'Bob',
            'last_name': 'User',
            'phone': '456',
            'from_city': 'Lviv',
            'to_city': 'Berlin',
            'departure_date': '2026-09-10',
            'seat_number': 7,
            'bus_number': 2,
            'baggage': False,
            'comments': 'test',
        })

        self.assertTrue(form.is_valid())
