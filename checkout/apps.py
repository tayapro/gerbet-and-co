from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    """
    Initializes signal handlers for synchronizing checkout-related data
    during the app's startup.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    def ready(self):
        import checkout.signals
