from django.urls import path
from . import views
from .webhooks import stripe_webhook


urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("cache_checkout_data/", views.cache_checkout_data,
         name="cache_checkout_data"),
    path("checkout_success/<uuid:order_id>/", views.checkout_success,
         name="checkout_success"),
    path("wh/", stripe_webhook, name="stripe_webhook")
]
