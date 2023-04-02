from django.db import models

class Restaurateur(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    resto_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'resto_name', 'phone_number']

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