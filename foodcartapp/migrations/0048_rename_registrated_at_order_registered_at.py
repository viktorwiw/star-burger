# Generated by Django 3.2.15 on 2025-02-11 21:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_order_restaurant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='registrated_at',
            new_name='registered_at',
        ),
    ]
