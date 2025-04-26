from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration class for the Accounts app.

    Handles app-specific setup, including importing signals
    to manage address defaults when a new address is saved.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import checkout.signals
