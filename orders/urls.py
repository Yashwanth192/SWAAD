from django.urls import path

from . import views

urlpatterns = [
    path('place/', views.place_order, name='place_order'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('complete/<int:order_id>/', views.complete_order, name='complete_order'),
    path('status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
