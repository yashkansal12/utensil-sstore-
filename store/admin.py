from django.contrib import admin

# Register your models here.
from .models import Utensil
from .models import Contact
from .models import Order


admin.site.register(Utensil)
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')  
    search_fields = ('name', 'email')
    list_filter = ('created_at',) 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'utensil', 'quantity', 'address', 'payment_method' )
    search_fields = ('name', 'phone')
    list_filter = ('ordered_at',)