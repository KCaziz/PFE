from django.contrib import admin
from app1.models import Product 

from .models import Reservation, Restaurant, Restaurateur, Cart, Order, Avis, Livraison

# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Restaurateur)
admin.site.register(Restaurant)
admin.site.register(Avis)
admin.site.register(Reservation)
admin.site.register(Livraison)
