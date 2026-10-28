from django.contrib import admin

from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'menu__food_name')
