from django.db.models import fields
from django import forms
from .models import Product, Avis, Reservation, Livraison


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

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nbr_tables', 'nbr_personnes', 'date', 'heure', 'commentaire']
        labels = {
            'nbr_tables': 'Nombre de tables',
            'nbr_personnes' : 'Nombre de personnes',
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['nbr_tables'].widget.attrs.update({'class': 'form-control'})
            self.fields['nbr_personnes'].widget.attrs.update({'class': 'form-control'})
            self.fields['date'].widget.attrs.update({'class': 'form-control'})
            self.fields['heure'].widget.attrs.update({'class': 'form-control'})
            self.fields['commentaire'].widget.attrs.update({'class': 'form-control'})


class LivraisonForm(forms.ModelForm):
    class Meta:
        model = Livraison
        fields = ('address', 'phone', 'heure')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['heure'].widget.attrs.update({'class': 'form-control'})


