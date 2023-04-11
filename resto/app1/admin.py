from django.contrib import admin
from app1.models import Product 

from .models import  Restaurateur

# Register your models here.
admin.site.register(Product)
admin.site.register(Restaurateur)
