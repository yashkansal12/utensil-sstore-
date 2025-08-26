from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Utensil(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description")
    price = models.FloatField()
    image = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    utensil = models.ForeignKey(Utensil, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.utensil.name}"
