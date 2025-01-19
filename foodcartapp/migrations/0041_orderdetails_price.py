# Generated by Django 3.2.15 on 2025-01-18 20:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20241227_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetails',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена продукта'),
        ),
    ]
