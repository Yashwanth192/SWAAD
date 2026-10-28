from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Menu, Vendor
from .models import CartItem


class CartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            password='test-password'
        )
        self.vendor_user = User.objects.create_user(
            username='vendor',
            password='test-password'
        )
        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            vendor_name='Vendor',
            restaurant_name='Test Restaurant',
            phone_num=9876543210,
            address1='1 Main Street',
            city='Test City',
            state='Test State',
            zipcode=123456,
            is_approved=True
        )
        self.menu = Menu.objects.create(
            vendor=self.vendor,
            food_name='Idli',
            price='50.00',
            category='Breakfast',
            is_available=True
        )
        self.client.login(username='customer', password='test-password')

    def test_add_to_cart_consolidates_quantity(self):
        url = reverse('cart_add', args=[self.menu.id])

        self.client.post(url)
        self.client.post(url)

        item = CartItem.objects.get(user=self.user, menu=self.menu)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(self.client.get(reverse('cart_detail')).status_code, 200)

    def test_unavailable_menu_cannot_be_added(self):
        self.menu.is_available = False
        self.menu.save(update_fields=['is_available'])

        response = self.client.post(reverse('cart_add', args=[self.menu.id]))

        self.assertEqual(response.status_code, 404)
        self.assertFalse(CartItem.objects.exists())

    def test_items_from_different_vendors_can_be_added(self):
        self.client.post(reverse('cart_add', args=[self.menu.id]))
        other_user = User.objects.create_user(
            username='other-vendor',
            password='test-password'
        )
        other_vendor = Vendor.objects.create(
            user=other_user,
            vendor_name='Other Vendor',
            restaurant_name='Other Restaurant',
            phone_num=9876543211,
            address1='2 Main Street',
            city='Test City',
            state='Test State',
            zipcode=123456,
            is_approved=True
        )
        other_menu = Menu.objects.create(
            vendor=other_vendor,
            food_name='Vada',
            price='30.00',
            category='Breakfast',
            is_available=True
        )

        response = self.client.post(reverse('cart_add', args=[other_menu.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 2)
        self.assertTrue(CartItem.objects.filter(menu=other_menu).exists())
