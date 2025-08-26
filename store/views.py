from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Utensil, Order

# Home Page
def index(request):
    return render(request, 'index.html')

# Register
def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password=password)
            return redirect('login')
        else:
            return render(request, 'register.html', {'error': 'Username already exists'})
    return render(request, 'register.html')

# Login
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('products')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

# Logout
def logout_user(request):
    logout(request)
    return redirect('index')

# Show all products
def products(request):
    if not request.user.is_authenticated:
        return redirect('login')
    items = Utensil.objects.all()
    return render(request, 'products.html', {'items': items})

# Add product to cart
def add_to_cart(request, utensil_id):
    if not request.user.is_authenticated:
        return redirect('login')

    utensil = get_object_or_404(Utensil, id=utensil_id)

    # Check if already in cart for this user
    order, created = Order.objects.get_or_create(user=request.user, utensil=utensil)
    if not created:
        order.quantity += 1  # Increase quantity if already added
        order.save()

    return redirect('cart')

# View cart
def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user)
    total_price = sum(order.utensil.price * order.quantity for order in orders)

    return render(request, 'cart.html', {'orders': orders, 'total_price': total_price})

# Buy Now (direct purchase)
def buy_now(request, utensil_id):
    if not request.user.is_authenticated:
        return redirect('login')

    utensil = get_object_or_404(Utensil, id=utensil_id)
    Order.objects.create(user=request.user, utensil=utensil, quantity=1)
    return redirect('cart')

# Remove item from cart
def remove_from_cart(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    return redirect('cart')
