# Generated by Django 4.1.7 on 2023-05-17 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0014_remove_livraison_order_livraison_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livraison',
            name='cart',
        ),
        migrations.AddField(
            model_name='livraison',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app1.order'),
        ),
    ]