from django.contrib import admin
from accounts.models import UserDetails, Vendor, Menu, Address, Favorite, Review


admin.site.register(UserDetails)
admin.site.register(Address)
admin.site.register(Favorite)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = ['vendor_name','restaurant_name','phone_num','city','state','is_approved',
    ]

    list_filter = [
        'is_approved',
        'city',
        'state',
    ]

    search_fields = [
        'vendor_name',
        'restaurant_name',
        'user__username',
        'user__email',
    ]


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):

    list_display = [
        'food_name',
        'price',
        'category',
        'vendor',
    ]

    list_filter = [
        'category',
    ]

    search_fields = [
        'food_name',
        'category',
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'vendor']
    search_fields = ['vendor__restaurant_name', 'user__username', 'comment']