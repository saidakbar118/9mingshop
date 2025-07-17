# forms.py
from django import forms

class OrderForm(forms.Form):
    full_name = forms.CharField(label="Ism", max_length=100)
    phone = forms.CharField(label="Telefon", max_length=20)
    address = forms.CharField(label="Manzil", widget=forms.Textarea)
