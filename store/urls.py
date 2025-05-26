from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    home, product_detail, category_view, CustomLoginView, register, custom_logout,
    search, about_us, contact_us, wishlist, add_to_wishlist, remove_from_wishlist,
    add_to_cart, remove_from_cart, update_cart, clear_cart, cart, user_profile,
    add_address, checkout, order_confirmation, returns, faqs, careers, privacy_policy,
    
)

urlpatterns = [
    path('', home, name='home'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('category/<int:category_id>/', category_view, name='category'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register, name='register'),
    path('search/', search, name='search'),
    path('about/', about_us, name='about_us'),
    path('contact/', contact_us, name='contact_us'),
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('cart/', cart, name='cart'),
    path('profile/', user_profile, name='profile'),
    path('address/add/', add_address, name='add_address'),
    path('checkout/', checkout, name='checkout'),
    path('order/<int:order_id>/', order_confirmation, name='order_confirmation'),
    path('returns/', returns, name='returns'),
    path('faqs/', faqs, name='faqs'),
    path('careers/', careers, name='careers'),
    path('privacy_policy/', privacy_policy, name='privacy_policy'),
]