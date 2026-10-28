from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import (
    UserForm,
    UserProfileForm,
    UserUpdateForm,
    UserProfileUpdateForm,
    VendorForm,
    MenuForm,
    AddressForm,
    ReviewForm,
)
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q

from accounts.models import UserDetails, Vendor, Menu, Favorite, Address, Review
from orders.models import Order


# =========================================================
# USER REGISTRATION
# =========================================================

def register(request):

    registered = False

    if request.method == 'POST':

        form1 = UserForm(request.POST)
        form2 = UserProfileForm(
            request.POST,
            request.FILES
        )

        if form1.is_valid() and form2.is_valid():

            user = form1.save()

            user.set_password(user.password)
            user.save()

            profile = form2.save(commit=False)
            profile.user = user
            profile.save()

            registered = True

    else:

        form1 = UserForm()
        form2 = UserProfileForm()

    return render(
        request,
        'registration.html',
        {
            'form1': form1,
            'form2': form2,
            'registered': registered
        }
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            username=username,
            password=password
        )

        if user:

            if user.is_active:

                login(request, user)

                # CHECK WHETHER USER IS VENDOR
                try:

                    vendor = Vendor.objects.get(
                        user=user
                    )

                    # Vendor approved
                    if vendor.is_approved:

                        return redirect(
                            'vendor_dashboard'
                        )

                    # Vendor not approved
                    else:

                        return redirect(
                            'vendor_pending'
                        )

                except Vendor.DoesNotExist:

                    # Normal user
                    return redirect('home')

            else:

                return HttpResponse(
                    "User is inactive"
                )

        else:

            return HttpResponse(
                "Please check your creds..!!"
            )

    return render(
        request,
        "login.html",
        {}
    )


# =========================================================
# HOME
# =========================================================

@login_required(login_url='login')
def home(request):

    top_vendors = Vendor.objects.filter(
        is_approved=True
    )

    search_query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if search_query:
        top_vendors = top_vendors.filter(
            Q(restaurant_name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(vendor_name__icontains=search_query)
        )

    if category:
        top_vendors = top_vendors.filter(
            menu_items__category__icontains=category
        ).distinct()

    categories = Menu.objects.filter(vendor__is_approved=True).values_list('category', flat=True).distinct()
    top_vendors = top_vendors.order_by('-id')[:12]

    current_vendor = Vendor.objects.filter(
        user=request.user
    ).first()

    return render(
        request,
        "home.html",
        {
            "top_vendors": top_vendors,
            "current_vendor": current_vendor,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category,
        }
    )


@login_required(login_url='login')
def restaurant_detail(request, id):

    vendor = get_object_or_404(
        Vendor,
        id=id,
        is_approved=True
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'toggle_favorite':
            favorite, created = Favorite.objects.get_or_create(user=request.user, vendor=vendor)
            if created:
                messages.success(request, f'Added {vendor.restaurant_name} to your favorites.')
            else:
                favorite.delete()
                messages.info(request, f'Removed {vendor.restaurant_name} from your favorites.')
            return redirect('restaurant_detail', id=id)

        if action == 'add_review':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                Review.objects.update_or_create(
                    user=request.user,
                    vendor=vendor,
                    defaults={
                        'rating': review_form.cleaned_data['rating'],
                        'comment': review_form.cleaned_data['comment'],
                    }
                )
                messages.success(request, 'Your review has been saved.')
            return redirect('restaurant_detail', id=id)

    menu_items = Menu.objects.filter(
        vendor=vendor,
        is_available=True
    )
    reviews = Review.objects.filter(vendor=vendor).select_related('user')
    is_favorite = Favorite.objects.filter(user=request.user, vendor=vendor).exists()
    existing_review = reviews.filter(user=request.user).first()
    review_form = ReviewForm(instance=existing_review) if existing_review else ReviewForm()

    return render(
        request,
        "restaurant_detail.html",
        {
            "vendor": vendor,
            "menu_items": menu_items,
            "reviews": reviews,
            "is_favorite": is_favorite,
            "review_form": review_form,
            "average_rating": vendor.average_rating(),
        }
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url='login')
def user_logout(request):

    logout(request)

    return redirect("login")


# =========================================================
# USER PROFILE
# =========================================================

@login_required(login_url="login")
def user_profile(request):

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_address':
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                if not Address.objects.filter(user=request.user, is_default=True).exists():
                    address.is_default = True
                address.save()
                messages.success(request, 'Address added successfully.')
            return redirect('profile')

        if action == 'set_default_address':
            address_id = request.POST.get('address_id')
            if address_id:
                Address.objects.filter(user=request.user).update(is_default=False)
                Address.objects.filter(user=request.user, id=address_id).update(is_default=True)
                messages.success(request, 'Default address updated.')
            return redirect('profile')

        if action == 'delete_address':
            address_id = request.POST.get('address_id')
            if address_id:
                Address.objects.filter(user=request.user, id=address_id).delete()
                messages.info(request, 'Address removed.')
            return redirect('profile')

    user_details, _ = UserDetails.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': 0,
            'age': 0,
            'house_no': 0,
            'street': '',
            'landmark': '',
            'city': '',
            'state': '',
            'zipcode': 0,
        }
    )

    user_orders = Order.objects.filter(
        user=request.user
    ).select_related('vendor').prefetch_related('items__menu').order_by('-created_at')

    address_form = AddressForm()
    saved_addresses = Address.objects.filter(user=request.user)
    favorite_vendors = Favorite.objects.filter(user=request.user).select_related('vendor')

    return render(
        request,
        "profile.html",
        {
            "user_orders": user_orders,
            "address_form": address_form,
            "saved_addresses": saved_addresses,
            "favorite_vendors": favorite_vendors,
            "user_details": user_details,
        }
    )


# =========================================================
# UPDATE USER PROFILE
# =========================================================

@login_required(login_url="login")
def update(request):

    user_details, _ = UserDetails.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': 0,
            'age': 0,
            'house_no': 0,
            'street': '',
            'landmark': '',
            'city': '',
            'state': '',
            'zipcode': 0,
        }
    )

    form1 = UserUpdateForm(
        instance=request.user
    )

    form2 = UserProfileUpdateForm(
        instance=user_details
    )

    if request.method == 'POST':

        form1 = UserUpdateForm(
            request.POST,
            instance=request.user
        )

        form2 = UserProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=user_details
        )

        if form1.is_valid() and form2.is_valid():

            user = form1.save()
            user.save()

            profile = form2.save(
                commit=False
            )

            profile.user = user
            profile.save()

            return redirect("profile")

    return render(
        request,
        "update.html",
        {
            'Form1': form1,
            'Form2': form2
        }
    )


# =========================================================
# VENDOR REGISTRATION
# =========================================================

@login_required(login_url="login")
def vendor_register(request):

    # If already registered as vendor
    if Vendor.objects.filter(
        user=request.user
    ).exists():

        return redirect(
            "vendor_pending"
        )

    if request.method == "POST":

        form = VendorForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            vendor = form.save(
                commit=False
            )

            # Connect vendor with current user
            vendor.user = request.user

            # Waiting for admin approval
            vendor.is_approved = False

            vendor.save()

            # Go to pending page
            return redirect(
                "vendor_pending"
            )

    else:

        form = VendorForm()

    return render(
        request,
        "vendor_register.html",
        {
            "form": form,
            "is_edit": False
        }
    )


@login_required(login_url="login")
def vendor_edit(request):

    vendor = get_object_or_404(
        Vendor,
        user=request.user
    )

    if request.method == "POST":

        form = VendorForm(
            request.POST,
            request.FILES,
            instance=vendor
        )

        if form.is_valid():
            form.save()
            return redirect("vendor_dashboard")

    else:

        form = VendorForm(instance=vendor)

    return render(
        request,
        "vendor_register.html",
        {
            "form": form,
            "is_edit": True
        }
    )


# =========================================================
# VENDOR PENDING
# =========================================================

@login_required(login_url="login")
def vendor_pending(request):

    try:

        vendor = Vendor.objects.get(
            user=request.user
        )

    except Vendor.DoesNotExist:

        return redirect(
            "vendor_register"
        )

    # If admin approved the vendor
    if vendor.is_approved:

        return redirect(
            "vendor_dashboard"
        )

    return render(
        request,
        "vendor_pending.html",
        {
            "vendor": vendor
        }
    )


# =========================================================
# VENDOR DASHBOARD
# =========================================================

@login_required(login_url="login")
def vendor_dashboard(request):

    try:

        vendor = Vendor.objects.get(
            user=request.user
        )

    except Vendor.DoesNotExist:

        return redirect(
            "vendor_register"
        )

    # Vendor cannot enter dashboard
    # until admin approves
    if not vendor.is_approved:

        return redirect(
            "vendor_pending"
        )

    menu_items = Menu.objects.filter(
        vendor=vendor
    )

    vendor_orders = Order.objects.filter(
        vendor=vendor
    ).select_related('user').prefetch_related('items__menu').order_by('-created_at')

    return render(
        request,
        "vendor_dashboard.html",
        {
            "vendor": vendor,
            "menu_items": menu_items,
            "vendor_orders": vendor_orders,
            "order_count": vendor_orders.count(),
            "open_order_count": vendor_orders.exclude(status="completed").count(),
            "menu_item_count": menu_items.count(),
            "available_menu_count": menu_items.filter(is_available=True).count(),
        }
    )


# =========================================================
# MENU LIST
# =========================================================

@login_required(login_url="login")
def menu_list(request):

    try:

        vendor = Vendor.objects.get(
            user=request.user
        )

    except Vendor.DoesNotExist:

        return redirect(
            "vendor_register"
        )

    if not vendor.is_approved:

        return redirect(
            "vendor_pending"
        )

    menu_items = Menu.objects.filter(
        vendor=vendor
    )

    return render(
        request,
        "menu_list.html",
        {
            "menu_items": menu_items
        }
    )


# =========================================================
# ADD MENU
# =========================================================

@login_required(login_url="login")
def menu_add(request):

    try:

        vendor = Vendor.objects.get(
            user=request.user
        )

    except Vendor.DoesNotExist:

        return redirect(
            "vendor_register"
        )

    if not vendor.is_approved:

        return redirect(
            "vendor_pending"
        )

    if request.method == "POST":

        form = MenuForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            menu = form.save(
                commit=False
            )

            menu.vendor = vendor

            menu.save()

            return redirect(
                "menu_list"
            )

    else:

        form = MenuForm()

    return render(
        request,
        "menu_add.html",
        {
            "form": form
        }
    )


# =========================================================
# EDIT MENU
# =========================================================

@login_required(login_url="login")
def menu_edit(request, id):

    vendor = Vendor.objects.get(
        user=request.user
    )

    if not vendor.is_approved:

        return redirect(
            "vendor_pending"
        )

    menu = get_object_or_404(Menu, id=id, vendor=vendor)

    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu)

        if form.is_valid():
            form.save()
            return redirect("menu_list")
    else:
        form = MenuForm(instance=menu)

    return render(
        request,
        "menu_edit.html",
        {
            "form": form,
            "menu": menu
        }
    )


# =========================================================
# TOGGLE MENU AVAILABILITY
# =========================================================

@login_required(login_url="login")
def menu_toggle_availability(request, id):

    vendor = Vendor.objects.get(
        user=request.user
    )

    if not vendor.is_approved:

        return redirect(
            "vendor_pending"
        )

    menu = get_object_or_404(Menu, id=id, vendor=vendor)

    if request.method == "POST":
        menu.is_available = not menu.is_available
        menu.save(update_fields=["is_available"])

        if menu.is_available:
            messages.success(request, f"{menu.food_name} is available to customers again.")
        else:
            messages.success(request, f"{menu.food_name} was removed from customer menus. You can restore it any time.")

    return redirect("menu_list" if request.POST.get("return_to") == "menu_list" else "vendor_dashboard")


# =========================================================
# ADMIN - VENDOR APPROVAL LIST
# =========================================================

@staff_member_required
def vendor_approval(request):

    vendors = Vendor.objects.filter(
        is_approved=False
    ).order_by('-id')

    return render(
        request,
        "vendor_approval.html",
        {
            "vendors": vendors
        }
    )


# =========================================================
# ADMIN - APPROVE VENDOR
# =========================================================

@staff_member_required
def approve_vendor(request, vendor_id):

    vendor = get_object_or_404(
        Vendor,
        id=vendor_id
    )

    vendor.is_approved = True
    vendor.save()

    messages.success(
        request,
        f"{vendor.restaurant_name} has been approved successfully."
    )

    return redirect(
        "vendor_approval"
    )


# =========================================================
# ADMIN - REJECT VENDOR
# =========================================================

@staff_member_required
def reject_vendor(request, vendor_id):

    vendor = get_object_or_404(
        Vendor,
        id=vendor_id
    )

    restaurant_name = vendor.restaurant_name

    vendor.delete()

    messages.success(
        request,
        f"{restaurant_name} has been rejected."
    )

    return redirect(
        "vendor_approval"
    )