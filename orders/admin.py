from django.contrib import admin
from orders.models import Order, OrderItem, Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'discount_percent',
        'minimum_order_amount',
        'vendor',
        'menu',
        'is_active',
        'valid_from',
        'valid_to',
    ]
    list_filter = ['is_active', 'vendor']
    search_fields = ['code', 'vendor__restaurant_name', 'menu__food_name']
    fields = [
        'code',
        'discount_percent',
        'minimum_order_amount',
        'vendor',
        'menu',
        'is_active',
        'valid_from',
        'valid_to',
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'vendor', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'vendor', 'created_at']
    search_fields = ['order_id', 'user__username', 'vendor__restaurant_name']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu', 'quantity', 'price']
