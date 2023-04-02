from django.contrib import admin

from .models import Consomation, Restaurateur

# Register your models here.

admin.site.register(Restaurateur)
admin.site.register(Consomation)
