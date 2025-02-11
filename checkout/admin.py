from django.contrib import admin
from .models import CheckoutConfig, ShippingInfo, Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "email", "total_price",
                    "status", "created_at", "stripe_pid")
    search_fields = ("order_id", "email", "user__username",
                     "stripe_pid")
    list_filter = ("status", "created_at")
    readonly_fields = ("order_id", "order_id", "created_at",
                       "stripe_pid")
    list_editable = ("status",)


@admin.register(CheckoutConfig)
class CheckoutConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'free_delivery_threshold', 'delivery_cost',
                    'stripe_currency')


@admin.register(ShippingInfo)
class ShippingInfoAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "street_address1",
                    "town_or_city", "country", "postcode")
    search_fields = ("full_name", "phone_number", "street_address1",
                     "town_or_city", "country", "postcode")
    list_filter = ("country", "town_or_city")
