# Generated by Django 5.1.5 on 2025-02-15 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0009_webhookevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhookevent',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
