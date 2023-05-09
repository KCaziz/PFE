from django.db.models import fields
from django import forms
from .models import Product, Avis


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'thumbnail']


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ('note', 'commentaire')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].widget.attrs.update({'class': 'form-control'})
        self.fields['commentaire'].widget.attrs.update({'class': 'form-control'})
