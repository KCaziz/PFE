from django.conf import settings
from django.db import models

from django.utils import timezone
from django.utils.text import slugify

class Restaurateur(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurateur'
    )
    
    def __str__(self):
        return self.user.username
    
class Restaurant(models.Model):

    proprietaire = models.ForeignKey('Restaurateur', on_delete=models.CASCADE, null=False, blank=True)
    resto_name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True, blank=True)
    phone_resto = models.CharField(max_length=15)
    mail_address = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    map_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.resto_name

class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True, editable=False)
    price = models.FloatField(default=0.0)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="products", blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='products')    # menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='products')
    #clé etrangère vers Menu pour avoir une relation oneToMany 
    def save(self, *args, **kwargs):
        if not self.id:
            # Si l'objet n'existe pas encore en base, générer le slug à partir de rest_name
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    

    


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)
    processed = models.BooleanField(default=False)


    def __str__(self) :
        return self.user.username
    
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order)

    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()

        self.orders.clear()
        super().delete(*args, **kwargs)

