# Generated by Django 4.1.7 on 2023-05-17 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0013_remove_livraison_cart_livraison_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livraison',
            name='order',
        ),
        migrations.AddField(
            model_name='livraison',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app1.cart'),
        ),
    ]
