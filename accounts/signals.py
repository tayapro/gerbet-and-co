# accounts/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import UserContactInfo
from checkout.models import ShippingInfo


@receiver(pre_save, sender=UserContactInfo)
def update_checkout_defaults(sender, instance, **kwargs):
    """
    Signal handlers for the accounts app.

    This module includes signals to automatically update related models.
    Currently, when a UserContactInfo instance is set as default,
    any existing default ShippingInfo instances for the same user
    are updated to non-default.
    """

    if instance.is_default:
        ShippingInfo.objects.filter(
            user=instance.user,
            is_default=True
        ).update(is_default=False)
