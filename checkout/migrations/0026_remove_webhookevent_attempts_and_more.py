# Generated by Django 5.1.5 on 2025-03-23 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0025_remove_order_stripe_payment_intent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webhookevent',
            name='attempts',
        ),
        migrations.RemoveField(
            model_name='webhookevent',
            name='last_error',
        ),
    ]
