from checkout.models import CheckoutConfig


def get_checkout_settings():
    settings, created = CheckoutConfig.objects.get_or_create(
        defaults={
            'free_delivery_threshold': 50.00,
            'delivery_cost': 5.00,
            'stripe_currency': 'eur',
        }
    )
    return settings
