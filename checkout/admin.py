from django.contrib import admin
from .models import CheckoutConfig, ShippingInfo, Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing Order entries.

    Displays key order details such as order ID, user, totals,
    status, and Stripe PaymentIntent ID. Supports search, filtering,
    and inline status editing.
    """

    list_display = ("order_id", "user", "guest_email", "grand_total",
                    "order_total", "delivery_cost",
                    "status", "created_at", "stripe_pid")
    search_fields = ("order_id", "guest_email", "user__username",
                     "stripe_pid")
    list_filter = ("status", "created_at")
    readonly_fields = ("order_id", "order_id", "created_at",
                       "stripe_pid")
    list_editable = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing OrderItem entries.

    Displays associated orders, products, quantities, and totals.
    Supports search, filtering, and read-only total fields.
    """

    list_display = ("order", "product", "quantity", "order_item_total")
    list_filter = ("order",)
    search_fields = ("order__order_id", "product__title")
    ordering = ("order",)
    readonly_fields = ("order_item_total",)


@admin.register(CheckoutConfig)
class CheckoutConfigAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing Checkout settings.

    Allows management of free delivery thresholds, delivery costs,
    and Stripe currency settings used during checkout.
    """

    list_display = ("id", "free_delivery_threshold", "delivery_cost",
                    "stripe_currency")


@admin.register(ShippingInfo)
class ShippingInfoAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing ShippingInfo entries.

    Displays and allows searching of user shipping details such as
    phone numbers, addresses, cities, and countries.
    """

    list_display = ("phone_number", "street_address1",
                    "town_or_city", "country", "postcode")
    search_fields = ("phone_number", "street_address1",
                     "town_or_city", "country", "postcode")
    list_filter = ("country", "town_or_city")
