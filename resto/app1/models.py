from django.conf import settings
from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.FloatField(default=0.0)
    description = models.TextField(blank=True)
    thubnail = models.ImageField(upload_to="products", blank=True, null=True)
class Restaurateur(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurateur'
    )
    resto_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=255, blank=True)

    def __str__(self):
        return self.resto_name

class Menu(models.Model):
    restaurateur=models.ForeignKey('Restaurateur', on_delete=models.CASCADE, null=True, blank=True)
    produits=models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)



