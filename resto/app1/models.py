from django.conf import settings
from django.db import models

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
    consomation=models.ForeignKey('Consomation', on_delete=models.CASCADE, null=True, blank=True)


class Consomation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name