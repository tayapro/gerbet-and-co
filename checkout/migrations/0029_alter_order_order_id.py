# Generated by Django 5.1.5 on 2025-04-11 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0028_delete_billinginfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(editable=False, max_length=20, unique=True),
        ),
    ]
