from django.urls import path

from . import views


urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('coupon/apply/', views.coupon_apply, name='coupon_apply'),
    path('add/<int:menu_id>/', views.cart_add, name='cart_add'),
    path('update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
]
