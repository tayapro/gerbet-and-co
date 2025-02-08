from django.contrib import admin
from .models import CheckoutConfig


@admin.register(CheckoutConfig)
class CheckoutConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'free_delivery_threshold', 'delivery_cost',
                    'stripe_currency')
