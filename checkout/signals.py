# from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import shipping_info_updated
from accounts.models import UserContactInfo
import logging


logger = logging.getLogger(__name__)


@receiver(shipping_info_updated)
def sync_profile_address(sender, instance, save_address_as_default=False,
                         **kwargs):
    """
    Signal handling for syncing shipping information with the user's address
    book.

    When a user saves a shipping address and chooses to mark it as default,
    this signal updates their profile with the new default address while
    ensuring data consistency across their saved addresses.
    """

    logger.info("Signal triggered for ShippingInfo.")

    # Ensure all required fields are present
    required_fields = [
        instance.phone_number,
        instance.street_address1,
        instance.town_or_city,
        instance.postcode,
        instance.country,
    ]

    if (
        all(required_fields)
        and not instance.is_default
        and save_address_as_default
        and instance.user
    ):
        # Create a new default address
        new_address = UserContactInfo.objects.create(
            user=instance.user,
            is_default=True,
            phone_number=instance.phone_number,
            street_address1=instance.street_address1,
            street_address2=instance.street_address2,
            town_or_city=instance.town_or_city,
            county=instance.county,
            postcode=instance.postcode,
            country=instance.country
        )

        # Update other addresses to no longer be default
        UserContactInfo.objects.filter(
            user=instance.user
        ).exclude(id=new_address.id).update(is_default=False)
    else:
        if not all(required_fields):
            logger.info("Signal ignored: Missing required fields.")
        if not instance.is_default:
            logger.info("Signal ignored: Address is not marked as default.")
        if not instance.user:
            logger.info("Signal ignored: No associated user.")
