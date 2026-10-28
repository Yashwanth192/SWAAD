from django.contrib.auth.models import User
from django.db import models

from accounts.models import Menu


class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'menu'],
                name='unique_cart_item_per_user'
            )
        ]

    @property
    def line_total(self):
        return self.menu.price * self.quantity

    def __str__(self):
        return f'{self.user.username}: {self.menu.food_name} x {self.quantity}'
