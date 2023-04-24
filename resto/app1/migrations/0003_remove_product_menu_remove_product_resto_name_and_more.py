# Generated by Django 4.1.4 on 2023-04-24 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_restaurant_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='menu',
        ),
        migrations.RemoveField(
            model_name='product',
            name='resto_name',
        ),
        migrations.AddField(
            model_name='product',
            name='restaurant',
            field=models.ForeignKey(default=0.00010001000100010001, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='app1.restaurant'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Menu',
        ),
    ]