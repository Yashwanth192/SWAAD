from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Menu, Vendor
from cart.models import CartItem
from orders.models import Coupon, Order


class OrderFlowTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='pass1234')
        self.vendor_user = User.objects.create_user(username='vendor', password='pass1234')
        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            vendor_name='Vendor One',
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
            food_name='Biriyani',
            price='120.00',
            category='Dinner',
            is_available=True,
        )
        self.client.login(username='customer', password='pass1234')

    def test_place_order_creates_unique_order_for_customer_and_vendor(self):
        self.client.post(reverse('cart_add', args=[self.menu.id]))

        response = self.client.post(reverse('place_order'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 0)

        order = Order.objects.get(user=self.customer, vendor=self.vendor)
        self.assertTrue(order.order_id.startswith('ORD-'))
        self.assertEqual(order.total_price, 120.00)
        self.assertEqual(order.status, Order.STATUS_PENDING)

        customer_profile = self.client.get(reverse('profile'))
        self.assertEqual(customer_profile.status_code, 200)
        self.assertContains(customer_profile, order.order_id)

        self.client.logout()
        self.client.login(username='vendor', password='pass1234')
        vendor_dashboard = self.client.get(reverse('vendor_dashboard'))
        self.assertEqual(vendor_dashboard.status_code, 200)
        self.assertContains(vendor_dashboard, order.order_id)

    def test_unavailable_item_in_cart_is_removed_before_checkout(self):
        other_menu = Menu.objects.create(
            vendor=self.vendor,
            food_name='Vada',
            price='30.00',
            category='Breakfast',
            is_available=True,
        )
        CartItem.objects.create(user=self.customer, menu=self.menu)
        CartItem.objects.create(user=self.customer, menu=other_menu)
        self.menu.is_available = False
        self.menu.save(update_fields=['is_available'])

        response = self.client.post(reverse('place_order'))

        self.assertRedirects(response, reverse('cart_detail'), fetch_redirect_response=False)
        self.assertFalse(Order.objects.filter(user=self.customer).exists())
        self.assertFalse(CartItem.objects.filter(user=self.customer, menu=self.menu).exists())
        self.assertTrue(CartItem.objects.filter(user=self.customer, menu=other_menu).exists())
        self.assertContains(
            self.client.get(reverse('cart_detail')),
            'These items are no longer available and were removed from your cart: Biriyani.'
        )

    def test_vendor_can_complete_order(self):
        self.client.post(reverse('cart_add', args=[self.menu.id]))
        self.client.post(reverse('place_order'))
        order = Order.objects.get(user=self.customer, vendor=self.vendor)

        self.client.logout()
        self.client.login(username='vendor', password='pass1234')
        response = self.client.get(reverse('complete_order', args=[order.id]))

        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_COMPLETED)

    def test_restaurant_coupon_minimum_only_discounts_target_restaurant(self):
        other_vendor_user = User.objects.create_user(username='other_vendor', password='pass1234')
        other_vendor = Vendor.objects.create(
            user=other_vendor_user,
            vendor_name='Other Vendor',
            restaurant_name='Other Restaurant',
            phone_num=9876543211,
            address1='Second Street',
            city='Test City',
            state='Test State',
            zipcode=123457,
            is_approved=True,
        )
        other_menu = Menu.objects.create(
            vendor=other_vendor,
            food_name='Soup',
            price='80.00',
            category='Dinner',
            is_available=True,
        )
        now = timezone.now()
        coupon = Coupon.objects.create(
            code='RESTAURANT20',
            discount_percent=20,
            minimum_order_amount='200.00',
            vendor=self.vendor,
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
        )
        CartItem.objects.create(user=self.customer, menu=self.menu, quantity=2)
        CartItem.objects.create(user=self.customer, menu=other_menu, quantity=1)

        response = self.client.post(reverse('place_order'), {'coupon_code': coupon.code})

        self.assertRedirects(response, reverse('profile'))
        target_order = Order.objects.get(user=self.customer, vendor=self.vendor)
        other_order = Order.objects.get(user=self.customer, vendor=other_vendor)
        self.assertEqual(target_order.discount_amount, Decimal('48.00'))
        self.assertEqual(target_order.coupon_code, coupon.code)
        self.assertEqual(other_order.discount_amount, Decimal('0.00'))
        self.assertEqual(other_order.coupon_code, '')

    def test_food_coupon_minimum_uses_only_target_food_subtotal(self):
        other_menu = Menu.objects.create(
            vendor=self.vendor,
            food_name='Side dish',
            price='150.00',
            category='Dinner',
            is_available=True,
        )
        now = timezone.now()
        coupon = Coupon.objects.create(
            code='BIRYANI20',
            discount_percent=20,
            minimum_order_amount='200.00',
            menu=self.menu,
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
        )
        CartItem.objects.create(user=self.customer, menu=self.menu, quantity=1)
        CartItem.objects.create(user=self.customer, menu=other_menu, quantity=1)

        response = self.client.post(reverse('place_order'), {'coupon_code': coupon.code})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cart_detail'))
        self.assertFalse(Order.objects.filter(user=self.customer).exists())
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 2)
        cart_response = self.client.get(reverse('cart_detail'))
        alert_text = 'Coupon BIRYANI20 requires at least ₹200.00 in eligible items.'
        self.assertContains(cart_response, alert_text)
        self.assertEqual(cart_response.content.count(alert_text.encode()), 1)
        cart_html = cart_response.content.decode()
        self.assertGreater(cart_html.index('cart-coupon-alert'), cart_html.index('Place Order'))

    def test_food_coupon_discounts_only_the_target_food(self):
        other_menu = Menu.objects.create(
            vendor=self.vendor,
            food_name='Side dish',
            price='150.00',
            category='Dinner',
            is_available=True,
        )
        now = timezone.now()
        coupon = Coupon.objects.create(
            code='BIRYANI10',
            discount_percent=10,
            minimum_order_amount='200.00',
            menu=self.menu,
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
        )
        CartItem.objects.create(user=self.customer, menu=self.menu, quantity=2)
        CartItem.objects.create(user=self.customer, menu=other_menu, quantity=1)

        self.client.post(reverse('place_order'), {'coupon_code': coupon.code})

        order = Order.objects.get(user=self.customer, vendor=self.vendor)
        self.assertEqual(order.subtotal, Decimal('390.00'))
        self.assertEqual(order.discount_amount, Decimal('24.00'))
        self.assertEqual(order.total_price, Decimal('366.00'))

    def test_apply_coupon_previews_discount_and_place_order_uses_it(self):
        now = timezone.now()
        coupon = Coupon.objects.create(
            code='SWAAD10',
            discount_percent=10,
            minimum_order_amount='100.00',
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
        )
        CartItem.objects.create(user=self.customer, menu=self.menu, quantity=2)

        response = self.client.post(reverse('coupon_apply'), {'coupon_code': coupon.code})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('cart_detail'))
        self.assertEqual(self.client.session['applied_coupon_code'], coupon.code)
        cart_response = self.client.get(reverse('cart_detail'))
        self.assertContains(cart_response, 'Apply coupon')
        self.assertContains(cart_response, 'SWAAD10 applied')
        self.assertContains(cart_response, '24.00')
        self.assertContains(cart_response, '216.00')

        self.client.post(reverse('place_order'), {'payment_method': 'cod'})

        order = Order.objects.get(user=self.customer, vendor=self.vendor)
        self.assertEqual(order.coupon_code, coupon.code)
        self.assertEqual(order.discount_amount, Decimal('24.00'))
        self.assertEqual(order.total_price, Decimal('216.00'))
        self.assertNotIn('applied_coupon_code', self.client.session)
