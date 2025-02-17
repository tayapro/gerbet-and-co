from django.contrib import admin
from .models import CheckoutConfig, ShippingInfo, Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "email", "grand_total",
                    "order_total", "delivery_cost",
                    "status", "created_at", "stripe_pid")
    search_fields = ("order_id", "email", "user__username",
                     "stripe_pid")
    list_filter = ("status", "created_at")
    readonly_fields = ("order_id", "order_id", "created_at",
                       "stripe_pid")
    list_editable = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin panel configuration for OrderItem model"""
    list_display = ('order', 'product', 'quantity', 'order_item_total')
    list_filter = ('order',)
    search_fields = ('order__order_id', 'product__title')
    ordering = ('order',)
    readonly_fields = ('order_item_total',)


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
