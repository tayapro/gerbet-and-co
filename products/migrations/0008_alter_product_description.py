# Generated by Django 5.1.5 on 2025-04-21 17:13

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_remove_product_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=tinymce.models.HTMLField(),
        ),
    ]
