from django.urls import path
from . import views
from .webhooks import stripe_webhook

"""
URL configuration for checkout-related views in the Gerbet & Co e-commerce
platform.

Includes routes for checkout processing, payment caching, order success
handling, and Stripe webhook integration.
"""

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("cache_checkout_data/", views.cache_checkout_data,
         name="cache_checkout_data"),
    path("checkout_success/<str:order_id>/", views.checkout_success,
         name="checkout_success"),
    path("wh/", stripe_webhook, name="stripe_webhook"),
]
