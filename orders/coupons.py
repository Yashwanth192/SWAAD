from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from .models import Coupon


def get_active_coupon(code):
    if not code:
        return None
    return Coupon.objects.filter(
        code__iexact=code.strip(),
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now(),
    ).first()


def eligible_coupon_items(coupon, items):
    if coupon.menu_id:
        return [item for item in items if item.menu_id == coupon.menu_id]
    if coupon.vendor_id:
        return [item for item in items if item.menu.vendor_id == coupon.vendor_id]
    return list(items)


def coupon_discount_for_items(coupon, items):
    subtotal = sum((item.line_total for item in items), Decimal('0.00'))
    return (subtotal * Decimal(coupon.discount_percent) / Decimal('100')).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )


def evaluate_coupon(coupon, items):
    eligible_items = eligible_coupon_items(coupon, items)
    eligible_subtotal = sum(
        (item.line_total for item in eligible_items),
        Decimal('0.00'),
    )

    if not eligible_items:
        return None, f'Coupon {coupon.code} does not apply to items in your cart.'

    if eligible_subtotal < coupon.minimum_order_amount:
        return None, (
            f'Coupon {coupon.code} requires at least ₹{coupon.minimum_order_amount} '
            'in eligible items.'
        )

    vendor_subtotals = defaultdict(lambda: Decimal('0.00'))
    for item in eligible_items:
        vendor_subtotals[item.menu.vendor_id] += item.line_total

    discount_amount = sum(
        (
            subtotal * Decimal(coupon.discount_percent) / Decimal('100')
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        for subtotal in vendor_subtotals.values()
    )

    return {
        'eligible_subtotal': eligible_subtotal,
        'discount_amount': discount_amount,
    }, ''