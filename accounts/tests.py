from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.models import Menu, UserDetails, Vendor


class UserProfileUpdateTests(TestCase):
    def test_update_view_creates_missing_profile_for_logged_in_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='yash', password='testpass123')

        self.client.force_login(user)

        response = self.client.get(reverse('update'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserDetails.objects.filter(user=user).exists())

    def test_profile_address_form_starts_collapsed(self):
        User = get_user_model()
        user = User.objects.create_user(username='yash', password='testpass123')
        self.client.force_login(user)

        response = self.client.get(reverse('profile'))

        self.assertContains(response, '<details class="address-form-card">', html=False)
        self.assertNotContains(response, '<details class="address-form-card" open>', html=False)

    def test_update_view_saves_uploaded_profile_picture(self):
        User = get_user_model()
        user = User.objects.create_user(username='yash', password='testpass123')
        details = UserDetails.objects.create(
            user=user,
            phone=1234567890,
            age=25,
            house_no=10,
            street='Main Road',
            landmark='Near Park',
            city='Bengaluru',
            state='Karnataka',
            zipcode=560001,
        )
        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='red').save(image_buffer, format='PNG')
        image = SimpleUploadedFile('profile.png', image_buffer.getvalue(), content_type='image/png')
        self.client.force_login(user)

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(reverse('update'), {
                'username': 'yash',
                'email': 'yash@example.com',
                'phone': '1234567890',
                'age': '25',
                'house_no': '10',
                'street': 'Main Road',
                'landmark': 'Near Park',
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'zipcode': '560001',
                'userpic': image,
            })

            details.refresh_from_db()
            self.assertRedirects(response, reverse('profile'))
            self.assertTrue(details.userpic)
            self.assertTrue(details.userpic.storage.exists(details.userpic.name))
            self.assertEqual(details.city, 'Bengaluru')
            self.assertEqual(details.street, 'Main Road')

            profile_response = self.client.get(reverse('profile'))
            self.assertContains(profile_response, 'Bengaluru')
            self.assertContains(profile_response, 'Main Road')
            self.assertContains(profile_response, details.userpic.url)

    def test_update_view_explains_invalid_submission(self):
        User = get_user_model()
        user = User.objects.create_user(username='yash', password='testpass123')
        User.objects.create_user(username='already_taken', password='testpass123')
        self.client.force_login(user)

        response = self.client.post(reverse('update'), {
            'username': 'already_taken',
            'email': 'yash@example.com',
            'phone': '1234567890',
            'age': '25',
            'house_no': '10',
            'street': 'Main Road',
            'landmark': 'Near Park',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'zipcode': '560001',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your profile was not updated.')
        self.assertContains(response, 'already exists')


class VendorMenuAvailabilityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='vendor',
            password='testpass123'
        )
        self.vendor = Vendor.objects.create(
            user=self.user,
            vendor_name='Test Vendor',
            restaurant_name='Test Restaurant',
            phone_num=9876543210,
            address1='Main Street',
            city='Test City',
            state='Test State',
            zipcode=123456,
            is_approved=True,
        )
        self.menu = Menu.objects.create(
            vendor=self.vendor,
            food_name='Idli',
            price='50.00',
            category='Breakfast',
            is_available=True,
        )
        self.client.force_login(self.user)

    def test_vendor_can_hide_and_restore_a_menu_item(self):
        url = reverse('menu_toggle_availability', args=[self.menu.id])

        hide_response = self.client.post(url)

        self.assertRedirects(hide_response, reverse('vendor_dashboard'))
        self.menu.refresh_from_db()
        self.assertFalse(self.menu.is_available)
        self.assertTrue(Menu.objects.filter(pk=self.menu.pk).exists())
        self.assertContains(self.client.get(reverse('vendor_dashboard')), 'Restore')

        restore_response = self.client.post(url)

        self.assertRedirects(restore_response, reverse('vendor_dashboard'))
        self.menu.refresh_from_db()
        self.assertTrue(self.menu.is_available)

    def test_old_delete_url_only_hides_the_item(self):
        response = self.client.post(reverse('menu_delete', args=[self.menu.id]))

        self.assertRedirects(response, reverse('vendor_dashboard'))
        self.menu.refresh_from_db()
        self.assertFalse(self.menu.is_available)
        self.assertTrue(Menu.objects.filter(pk=self.menu.pk).exists())
