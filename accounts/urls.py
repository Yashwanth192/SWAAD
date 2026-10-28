from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from accounts import views


urlpatterns = [

    # User
    path('', RedirectView.as_view(pattern_name='register'), name='root'),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name="login"),
    path('home/', views.home, name="home"),
    path('restaurant/<int:id>/', views.restaurant_detail, name="restaurant_detail"),
    path('logout/', views.user_logout, name="logout"),
    path('profile/', views.user_profile, name="profile"),
    path('update/', views.update, name="update"),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        success_url='done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/password-reset/complete/'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Vendor
    path(
        'vendor/register/',
        views.vendor_register,
        name="vendor_register"
    ),

    path(
        'vendor/edit/',
        views.vendor_edit,
        name="vendor_edit"
    ),

    path(
        'vendor/dashboard/',
        views.vendor_dashboard,
        name="vendor_dashboard"
    ),

    path(
        'vendor/pending/',
        views.vendor_pending,
        name="vendor_pending"
    ),

    # Menu
    path(
        'menu/',
        views.menu_list,
        name="menu_list"
    ),

    path(
        'menu/add/',
        views.menu_add,
        name="menu_add"
    ),

    path(
        'menu/edit/<int:id>/',
        views.menu_edit,
        name="menu_edit"
    ),

    path(
        'menu/<int:id>/availability/',
        views.menu_toggle_availability,
        name="menu_toggle_availability"
    ),
    path(
        'menu/delete/<int:id>/',
        views.menu_toggle_availability,
        name="menu_delete"
    ),
]