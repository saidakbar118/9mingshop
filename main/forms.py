# forms.py
from django import forms
from .models import *

class OrderForm(forms.Form):
    full_name = forms.CharField(label="Ism", max_length=100)
    phone = forms.CharField(label="Telefon", max_length=20)
    address = forms.CharField(label="Manzil", widget=forms.Textarea)
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'image', 'old_price', 'price', 'is_free']
