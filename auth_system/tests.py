from django.contrib.auth import get_user_model
from django.test import TestCase

from Transportation_APP.forms import BookingForm
from Transportation_APP.models import Booking


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

    def test_booking_page_accepts_preselected_seat_for_logged_user(self):
        self.client.login(username='testuser', password='pass12345')
        response = self.client.get('/booking/?seat=4')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="4"')

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
