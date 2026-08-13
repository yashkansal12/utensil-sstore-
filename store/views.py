from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Utensil
from .models import Order
from .models import Contact
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UtensilForm
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages

# Home Page
def index(request):
    return render(request, 'index.html')

# Register
def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # OPTIONAL: Store additional fields if you have Profile Model
        # Example:
        # user.profile.phone = phone
        # user.profile.address = address
        # user.profile.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "register.html")

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
    order, created = Order.objects.get_or_create(
        user=request.user,
        utensil=utensil, 
        ordered=False,
        defaults={"quantity": 1}
    )
    if not created:
        order.quantity += 1  # Increase quantity if already added
        order.save()

    return redirect('cart')

# View cart
def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user, ordered=False)
    total_price = sum(order.utensil.price * order.quantity for order in orders)

    return render(request, 'cart.html', {'orders': orders, 'total_price': total_price})

# Buy Now (direct purchase)
def buy_now(request, utensil_id):
    if not request.user.is_authenticated:
        return redirect('login')

    utensil = get_object_or_404(Utensil, id=utensil_id)
    Order.objects.create(
        user=request.user,
        utensil=utensil,
        quantity=1,
        ordered=True
    )
    
    return redirect('checkout')

# Remove item from cart
def remove_from_cart(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, user=request.user, ordered=False)
    order.delete()
    return redirect('cart')

# Search button 
def search(request):
    query = request.GET.get('q')  # get search text
    results = []

    if query:
        results = Utensil.objects.filter(name__icontains=query)  # case-insensitive match

    return render(request, 'store/search.html', {'query': query, 'results': results})
 # my orders
def my_orders(request):
    orders = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_at')
    return render(request, 'my_orders.html', {'orders': orders})
# account
def account(request):
    orders = request.user.order_set.all().order_by('-ordered_at')  # user ke saare orders
    return render(request, 'account.html', {'orders': orders})

# for update in quantity in cart
def update_quantity(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "increase":
            order.quantity += 1
            order.save()
        elif action == "decrease":
            if order.quantity > 1:
                order.quantity -= 1
                order.save()
        elif action == "remove":
            order.delete()

    return redirect("cart")

# for contact
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # ✅ Save into DB
        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        return render(request, "thankyou_Contact.html")

    return render(request, "Contact.html") 

# for order checkout 
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user, ordered=False)
    total_price = sum(order.utensil.price * order.quantity for order in orders)

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        payment_method = request.POST.get("payment_method")

        for order in orders:
            order.name = name
            order.address = address
            order.phone = phone
            order.payment_method = payment_method
            order.ordered = True
            order.save()

            

        return render(request, "thankyou.html", {"name": name, "total_price": total_price})
    return render(request, "checkout.html", {"orders": orders, "total_price": total_price})


# Check if user is staff (seller)
def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)  # only staff can access
def add_product(request):
    if request.method == "POST":
        form = UtensilForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("products")  # redirect to products page
    else:
        form = UtensilForm()

    return render(request, "add_product.html", {"form": form})


# ✅ Edit Product
@login_required
@user_passes_test(is_staff_user)
def edit_product(request, pk):
    product = get_object_or_404(Utensil, pk=pk)
    if request.method == "POST":
        form = UtensilForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products")  # redirect after update
    else:
        form = UtensilForm(instance=product)

    return render(request, "edit_product.html", {"form": form, "product": product})

# download invoice
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # PDF response create karna
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)

    # Invoice heading
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Invoice - Utensil Store")

    # Order details
    p.setFont("Helvetica", 12)
    p.drawString(50, 750, f"Order ID: {order.id}")
    p.drawString(50, 730, f"Customer: {request.user.username}")
    p.drawString(50, 710, f"Product: {order.utensil.name}")
    p.drawString(50, 690, f"Quantity: {order.quantity}")
    p.drawString(50, 670, f"Price: ₹{order.utensil.price}")
    p.drawString(50, 650, f"Total: ₹{order.utensil.price * order.quantity}")

    # Footer
    p.drawString(200, 600, "Thank you for shopping with us!")

    p.showPage()
    p.save()
    return response
    
# update order
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if timezone.now() - order.ordered_at > timedelta(days=5):
        messages.error(request, "❌ You can no longer update this order (time limit exceeded).")
        return redirect('my_orders')
    # your update form logic here
# cancel order
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if timezone.now() - order.ordered_at > timedelta(days=5):
        messages.error(request, "❌ You can no longer cancel this order (time limit exceeded).")
        return redirect('my_orders')
    order.delete()
    messages.success(request, "✅ Your order has been cancelled successfully.")
    return redirect('my_orders')








# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login, logout
# from .models import Utensil
# from .models import Order
# from .models import Contact
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required, user_passes_test
# from .forms import UtensilForm
# from reportlab.pdfgen import canvas
# from django.http import HttpResponse
# from datetime import timedelta
# from django.utils import timezone
# from django.contrib import messages

# # Home Page
# def index(request):
#     return render(request, 'index.html')

# # Register
# def register_user(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         if not User.objects.filter(username=username).exists():
#             User.objects.create_user(username=username, password=password)
#             return redirect('login')
#         else:
#             return render(request, 'register.html', {'error': 'Username already exists'})
#     return render(request, 'register.html')

# # Login
# def login_user(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect('products')
#         else:
#             return render(request, 'login.html', {'error': 'Invalid username or password'})
#     return render(request, 'login.html')

# # Logout
# def logout_user(request):
#     logout(request)
#     return redirect('index')

# # Show all products
# def products(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#     items = Utensil.objects.all()
#     return render(request, 'products.html', {'items': items})

# # Add product to cart
# def add_to_cart(request, utensil_id):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     utensil = get_object_or_404(Utensil, id=utensil_id)

#     # Check if already in cart for this user
#     order, created = Order.objects.get_or_create(
#         user=request.user,
#         utensil=utensil, 
#         ordered=False,
#         defaults={"quantity": 1}
#     )
#     if not created:
#         order.quantity += 1  # Increase quantity if already added
#         order.save()

#     return redirect('cart')

# # View cart
# def view_cart(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     orders = Order.objects.filter(user=request.user, ordered=False)
#     total_price = sum(order.utensil.price * order.quantity for order in orders)

#     return render(request, 'cart.html', {'orders': orders, 'total_price': total_price})

# # Buy Now (direct purchase)
# def buy_now(request, utensil_id):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     utensil = get_object_or_404(Utensil, id=utensil_id)
#     Order.objects.create(
#         user=request.user,
#         utensil=utensil,
#         quantity=1,
#         ordered=True
#     )
    
#     return redirect('checkout')

# # Remove item from cart
# def remove_from_cart(request, order_id):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     order = get_object_or_404(Order, id=order_id, user=request.user, ordered=False)
#     order.delete()
#     return redirect('cart')

# # Search button 
# def search(request):
#     query = request.GET.get('q')  # get search text
#     results = []

#     if query:
#         results = Utensil.objects.filter(name__icontains=query)  # case-insensitive match

#     return render(request, 'store/search.html', {'query': query, 'results': results})
#  # my orders
# def my_orders(request):
#     orders = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_at')
#     return render(request, 'my_orders.html', {'orders': orders})
# # account
# def account(request):
#     orders = request.user.order_set.all().order_by('-ordered_at')  # user ke saare orders
#     return render(request, 'account.html', {'orders': orders})

# # for update in quantity in cart
# def update_quantity(request, order_id):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     order = get_object_or_404(Order, id=order_id, user=request.user)

#     if request.method == "POST":
#         action = request.POST.get("action")
#         if action == "increase":
#             order.quantity += 1
#             order.save()
#         elif action == "decrease":
#             if order.quantity > 1:
#                 order.quantity -= 1
#                 order.save()
#         elif action == "remove":
#             order.delete()

#     return redirect("cart")

# # for contact
# def contact_view(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         message = request.POST.get("message")

#         # ✅ Save into DB
#         Contact.objects.create(
#             name=name,
#             email=email,
#             message=message
#         )

#         return render(request, "thankyou_Contact.html")

#     return render(request, "Contact.html") 

# # for order checkout 
# def checkout(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     orders = Order.objects.filter(user=request.user, ordered=False)
#     total_price = sum(order.utensil.price * order.quantity for order in orders)

#     if request.method == "POST":
#         name = request.POST.get("name")
#         address = request.POST.get("address")
#         phone = request.POST.get("phone")
#         payment_method = request.POST.get("payment_method")

#         for order in orders:
#             order.name = name
#             order.address = address
#             order.phone = phone
#             order.payment_method = payment_method
#             order.ordered = True
#             order.save()

            

#         return render(request, "thankyou.html", {"name": name, "total_price": total_price})
#     return render(request, "checkout.html", {"orders": orders, "total_price": total_price})


# # Check if user is staff (seller)
# def is_staff_user(user):
#     return user.is_staff

# @login_required
# @user_passes_test(is_staff_user)  # only staff can access
# def add_product(request):
#     if request.method == "POST":
#         form = UtensilForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("products")  # redirect to products page
#     else:
#         form = UtensilForm()

#     return render(request, "add_product.html", {"form": form})


# # ✅ Edit Product
# @login_required
# @user_passes_test(is_staff_user)
# def edit_product(request, pk):
#     product = get_object_or_404(Utensil, pk=pk)
#     if request.method == "POST":
#         form = UtensilForm(request.POST, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect("products")  # redirect after update
#     else:
#         form = UtensilForm(instance=product)

#     return render(request, "edit_product.html", {"form": form, "product": product})

# # download invoice
# @login_required
# def download_invoice(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)

#     # PDF response create karna
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

#     p = canvas.Canvas(response)

#     # Invoice heading
#     p.setFont("Helvetica-Bold", 16)
#     p.drawString(200, 800, "Invoice - Utensil Store")

#     # Order details
#     p.setFont("Helvetica", 12)
#     p.drawString(50, 750, f"Order ID: {order.id}")
#     p.drawString(50, 730, f"Customer: {request.user.username}")
#     p.drawString(50, 710, f"Product: {order.utensil.name}")
#     p.drawString(50, 690, f"Quantity: {order.quantity}")
#     p.drawString(50, 670, f"Price: ₹{order.utensil.price}")
#     p.drawString(50, 650, f"Total: ₹{order.utensil.price * order.quantity}")

#     # Footer
#     p.drawString(200, 600, "Thank you for shopping with us!")

#     p.showPage()
#     p.save()
#     return response
    
# # update order
# def update_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     if timezone.now() - order.ordered_at > timedelta(days=5):
#         messages.error(request, "❌ You can no longer update this order (time limit exceeded).")
#         return redirect('my_orders')
#     # your update form logic here
# # cancel order
# def cancel_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     if timezone.now() - order.ordered_at > timedelta(days=5):
#         messages.error(request, "❌ You can no longer cancel this order (time limit exceeded).")
#         return redirect('my_orders')
#     order.delete()
#     messages.success(request, "✅ Your order has been cancelled successfully.")
#     return redirect('my_orders')

