from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Utensil(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description")
    price = models.FloatField()
    image = models.URLField(blank=True)
    category = models.CharField(max_length=50, default="General")

    def __str__(self):
        return self.name

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     utensil = models.ForeignKey(Utensil, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     ordered_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.utensil.name}"
    
# class Order(models.Model):
#     PAYMENT_CHOICES = [
#         ('cod', 'Cash on Delivery'),
#         ('upi', 'UPI'),
#         ('card', 'Credit/Debit Card'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     utensil = models.ForeignKey(Utensil, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=0)
#     name = models.CharField(max_length=100, blank=True)
#     address = models.TextField(blank=True)
#     phone = models.CharField(max_length=15, blank=True)
#     payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, blank=True)
#     ordered = models.BooleanField(default=False)
#     ordered_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.utensil.name} × {self.quantity}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    utensil = models.ForeignKey(Utensil, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.utensil.name} ({self.quantity})"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    utensil = models.ForeignKey(Utensil, on_delete=models.CASCADE)  # keep utensil here
    quantity = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.utensil.name} × {self.quantity}"


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

        