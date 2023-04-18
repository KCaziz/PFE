from django.db.models import fields
from django import forms
from .models import Product

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Product
        fields="__all__"