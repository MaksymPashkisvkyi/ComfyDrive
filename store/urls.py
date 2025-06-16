# store/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/', views.order_view, name='order_view'),

    # інформсторінки
    path('about/', views.about_view, name='about'),
    path('delivery/', views.delivery_view, name='delivery'),
    path('contacts/', views.contacts_view, name='contacts'),
]
