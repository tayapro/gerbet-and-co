# Generated by Django 5.1.5 on 2025-02-08 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DeliveryConfig',
            new_name='DeliveryCosts',
        ),
        migrations.AlterModelOptions(
            name='deliverycosts',
            options={'verbose_name': 'Delivery Costs', 'verbose_name_plural': 'Delivery Costs'},
        ),
    ]
