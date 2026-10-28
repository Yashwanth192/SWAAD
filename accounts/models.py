from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UserDetails(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    # additional fields
    phone = models.BigIntegerField()
    age = models.PositiveIntegerField()
    house_no = models.IntegerField()
    street = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.IntegerField()

    userpic = models.ImageField(
        upload_to='userimg/',
        blank=True,
        null=True
    )


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')
    house_no = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_default', 'id']

    def __str__(self):
        return f'{self.user.username} - {self.label}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'vendor'], name='unique_favorite_vendor')
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.vendor.restaurant_name}'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'vendor'], name='unique_review_per_user_vendor')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} rated {self.vendor.restaurant_name} {self.rating}/5'


# Vendor
class Vendor(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    # Vendor registration details
    vendor_name = models.CharField(
        max_length=200
    )

    restaurant_name = models.CharField(
        max_length=200
    )

    phone_num = models.BigIntegerField()

    address1 = models.CharField(
        max_length=200
    )

    address2 = models.CharField(
        max_length=200,
        blank=True
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    zipcode = models.IntegerField()

    gst_no = models.CharField(
        max_length=50,
        blank=True
    )

    licence_img = models.ImageField(
        upload_to='licence/',
        blank=True,
        null=True
    )

    restaurant_img = models.ImageField(
        upload_to='restaurant_image/',
        blank=True,
        null=True
    )

    is_approved = models.BooleanField(
        default=False
    )
    cuisine = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    delivery_time = models.CharField(max_length=50, blank=True)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    opening_hours = models.CharField(max_length=100, blank=True)

    def average_rating(self):
        average = self.reviews.aggregate(avg=models.Avg('rating'))['avg']
        return float(average) if average is not None else 0

    def __str__(self):
        return self.restaurant_name


# Menu
class Menu(models.Model):

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )

    food_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    category = models.CharField(
        max_length=100
    )

    # Added for menu CRUD
    food_image = models.ImageField(
        upload_to='food/',
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    is_available = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.food_name