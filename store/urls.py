from django.urls import path
from . import views

from django.contrib import admin

# Change site header, title, and index text
admin.site.site_header = "Utensil Store Admin"
admin.site.site_title = "Utensil Store Admin Portal"
admin.site.index_title = "Welcome to Utensil Store Dashboard"


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('products/', views.products, name='products'),
    path('add-to-cart/<int:utensil_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:utensil_id>/', views.buy_now, name='buy_now'),
    path('cart/', views.view_cart, name='cart'),
    path('remove-from-cart/<int:order_id>/', views.remove_from_cart, name='remove_from_cart'),

]
