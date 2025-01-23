# Generated by Django 3.2.15 on 2025-01-23 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20250123_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличностью'), ('electronic', 'Электронно')], db_index=True, default='cash', max_length=20, verbose_name='Способ оплаты'),
        ),
    ]
