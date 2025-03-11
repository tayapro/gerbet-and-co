from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ShippingInfo
from accounts.models import UserContactInfo
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=ShippingInfo)
def sync_profile_address(sender, instance, created, **kwargs):
    """
    Sync shipping info with user's contact info when:
    - User is authenticated
    - User chooses to save as default address
    - All required fields are populated
    """
    logger.info("Signal triggered for ShippingInfo.")
    print("Signal triggered!")

    # Log relevant details for debugging
    print(f"user: {instance.user}")
    print(f"phone_number: {instance.phone_number}")
    print(f"street_address1: {instance.street_address1}")
    print(f"street_address2: {instance.street_address2}")
    print(f"town_or_city: {instance.town_or_city}")
    print(f"county: {instance.county}")
    print(f"postcode: {instance.postcode}")
    print(f"country: {instance.country}")

    # Ensure all required fields are present
    required_fields = [
        instance.phone_number,
        instance.street_address1,
        instance.town_or_city,
        instance.postcode,
        instance.country,
    ]

    if all(required_fields) and instance.is_default and instance.user:
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
        print(f"New default address created with ID {new_address.id}")

        # Update other addresses to no longer be default
        UserContactInfo.objects.filter(
            user=instance.user
        ).exclude(id=new_address.id).update(is_default=False)
        print("Updated other addresses to is_default=False")
    else:
        if not all(required_fields):
            print("Signal ignored: Missing required fields.")
        if not instance.is_default:
            print("Signal ignored: Address is not marked as default.")
        if not instance.user:
            print("Signal ignored: No associated user.")
