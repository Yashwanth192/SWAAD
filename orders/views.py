from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import CartItem
from orders.coupons import coupon_discount_for_items, evaluate_coupon, get_active_coupon
from orders.models import Order, OrderItem


@login_required(login_url='login')
def place_order(request):
    if request.method != 'POST':
        return redirect('cart_detail')

    items = list(CartItem.objects.select_related('menu', 'menu__vendor').filter(user=request.user))
    if not items:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart_detail')

    unavailable_items = [item for item in items if not item.menu.is_available]
    if unavailable_items:
        unavailable_ids = [item.id for item in unavailable_items]
        unavailable_names = ', '.join(item.menu.food_name for item in unavailable_items)
        CartItem.objects.filter(id__in=unavailable_ids).delete()
        messages.warning(
            request,
            f'These items are no longer available and were removed from your cart: {unavailable_names}.'
        )
        return redirect('cart_detail')

    grouped_items = defaultdict(list)
    for item in items:
        grouped_items[item.menu.vendor].append(item)

    coupon_code = request.POST.get('coupon_code', '').strip() or request.session.get('applied_coupon_code', '')
    coupon_obj = None
    if coupon_code:
        coupon_obj = get_active_coupon(coupon_code)
        if coupon_obj is None:
            request.session.pop('applied_coupon_code', None)
            messages.warning(request, 'Coupon code is invalid or expired.')
            return redirect('cart_detail')

        _, error = evaluate_coupon(coupon_obj, items)
        if error:
            request.session.pop('applied_coupon_code', None)
            request.session['cart_coupon_alert'] = error
            return redirect('cart_detail')

    created_orders = []
    for vendor, vendor_items in grouped_items.items():
        subtotal = sum((item.line_total for item in vendor_items), 0)
        discount_amount = Decimal('0.00')
        if coupon_obj is not None:
            eligible_vendor_items = vendor_items
            if coupon_obj.vendor_id and coupon_obj.vendor_id != vendor.id:
                eligible_vendor_items = []
            elif coupon_obj.menu_id:
                eligible_vendor_items = [item for item in vendor_items if item.menu_id == coupon_obj.menu_id]

            discount_amount = coupon_discount_for_items(coupon_obj, eligible_vendor_items)
        order_total = subtotal - discount_amount

        order = Order.objects.create(
            user=request.user,
            vendor=vendor,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_price=order_total,
            coupon_code=coupon_obj.code if discount_amount else '',
            payment_method=request.POST.get('payment_method', 'cod'),
        )

        for item in vendor_items:
            OrderItem.objects.create(
                order=order,
                menu=item.menu,
                quantity=item.quantity,
                price=item.menu.price,
            )

        created_orders.append(order)

    CartItem.objects.filter(user=request.user).delete()
    request.session.pop('applied_coupon_code', None)

    order_ids = ', '.join(order.order_id for order in created_orders)
    messages.success(request, f'Order placed successfully. Order ID(s): {order_ids}')
    return redirect('profile')


@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related('user', 'vendor').prefetch_related('items__menu'), id=order_id)

    if request.user != order.user and request.user != order.vendor.user:
        raise PermissionDenied

    return render(request, 'order.html', {'order': order})


@login_required(login_url='login')
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, vendor__user=request.user)

    if order.status in [Order.STATUS_CANCELLED, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]:
        messages.info(request, f'Order {order.order_id} is already in a completed state.')
        return redirect('vendor_dashboard')

    order.status = Order.STATUS_COMPLETED
    order.save(update_fields=['status'])
    messages.success(request, f'Order {order.order_id} marked as completed.')
    return redirect('vendor_dashboard')


@login_required(login_url='login')
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, vendor__user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Order {order.order_id} updated to {new_status.replace("_", " ").title()}.')
        else:
            messages.warning(request, 'Invalid order status selected.')
    return redirect('order_detail', order_id=order.id)
