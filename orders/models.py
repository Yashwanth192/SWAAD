import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import Menu, Vendor


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='coupons',
        blank=True,
        null=True,
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='coupons',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now)

    def clean(self):
        super().clean()
        if self.vendor_id and self.menu_id:
            raise ValidationError('Choose either a restaurant or a food item for this coupon, not both.')

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PREPARING = 'preparing'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_OUT_FOR_DELIVERY, 'Out for delivery'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    coupon_code = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=20, default='cod')
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            timestamp = timezone.now().strftime('%d%m%y%H%M%S')
            random_code = uuid.uuid4().hex[:6].upper()
            self.order_id = f'ORD-{timestamp}-{random_code}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.order_id} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.order.order_id} - {self.menu.food_name}'
