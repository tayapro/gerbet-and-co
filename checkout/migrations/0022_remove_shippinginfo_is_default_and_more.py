# Generated by Django 5.1.5 on 2025-03-11 13:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_usercontactinfo_is_default'),
        ('checkout', '0021_alter_shippinginfo_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippinginfo',
            name='is_default',
        ),
        migrations.AddField(
            model_name='shippinginfo',
            name='original_default',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.usercontactinfo', verbose_name='Original Default Address'),
        ),
    ]
