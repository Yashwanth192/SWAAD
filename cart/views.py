from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Menu
from .models import CartItem
from orders.coupons import evaluate_coupon, get_active_coupon


@login_required(login_url='login')
def cart_add(request, menu_id):
    if request.method != 'POST':
        return redirect('cart_detail')

    menu = get_object_or_404(Menu, id=menu_id, is_available=True)
    item, created = CartItem.objects.get_or_create(
        user=request.user,
        menu=menu,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity = F('quantity') + 1
        item.save(update_fields=['quantity'])

    messages.success(request, f'{menu.food_name} added to your cart.')
    return redirect('restaurant_detail', id=menu.vendor_id)


@login_required(login_url='login')
def cart_detail(request):
    items = list(CartItem.objects.select_related('menu', 'menu__vendor').filter(user=request.user))
    subtotal = sum((item.line_total for item in items), 0)
    coupon_alert = request.session.pop('cart_coupon_alert', '')
    applied_coupon_code = request.session.get('applied_coupon_code', '')
    applied_coupon = get_active_coupon(applied_coupon_code)
    coupon_discount = 0

    if applied_coupon_code and applied_coupon is None:
        request.session.pop('applied_coupon_code', None)
        applied_coupon_code = ''
        messages.warning(request, 'The applied coupon is no longer valid.')
    elif applied_coupon:
        preview, error = evaluate_coupon(applied_coupon, items)
        if error:
            request.session.pop('applied_coupon_code', None)
            applied_coupon = None
            applied_coupon_code = ''
            coupon_alert = error
        else:
            coupon_discount = preview['discount_amount']

    return render(request, 'cart/detail.html', {
        'cart_items': items,
        'cart_subtotal': subtotal,
        'coupon_discount': coupon_discount,
        'cart_total': subtotal - coupon_discount,
        'applied_coupon': applied_coupon,
        'applied_coupon_code': applied_coupon_code,
        'coupon_alert': coupon_alert,
    })


@login_required(login_url='login')
def coupon_apply(request):
    if request.method != 'POST':
        return redirect('cart_detail')

    request.session.pop('cart_coupon_alert', None)
    coupon_code = request.POST.get('coupon_code', '').strip()
    items = list(CartItem.objects.select_related('menu', 'menu__vendor').filter(user=request.user))
    coupon = get_active_coupon(coupon_code)

    if coupon is None:
        request.session.pop('applied_coupon_code', None)
        messages.warning(request, 'Coupon code is invalid or expired.')
        return redirect('cart_detail')

    preview, error = evaluate_coupon(coupon, items)
    if error:
        request.session.pop('applied_coupon_code', None)
        request.session['cart_coupon_alert'] = error
        return redirect('cart_detail')

    request.session['applied_coupon_code'] = coupon.code
    request.session.pop('cart_coupon_alert', None)
    messages.success(request, f'Coupon {coupon.code} applied. You save ₹{preview["discount_amount"]}.')
    return redirect('cart_detail')


@login_required(login_url='login')
def cart_update(request, item_id):
    if request.method != 'POST':
        return redirect('cart_detail')

    item = CartItem.objects.filter(id=item_id, user=request.user).first()
    if item is None:
        messages.warning(request, 'This cart item is no longer available.')
        return redirect('cart_detail')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        item.delete()
    else:
        item.quantity = min(quantity, 99)
        item.save(update_fields=['quantity'])
    return redirect('cart_detail')


@login_required(login_url='login')
def cart_remove(request, item_id):
    if request.method == 'POST':
        CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('cart_detail')
