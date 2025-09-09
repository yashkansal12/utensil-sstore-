from django import forms
from .models import Utensil

class UtensilForm(forms.ModelForm):
    class Meta:
        model = Utensil
        fields = ['name', 'description', 'price', 'image']
