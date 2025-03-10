from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ShippingInfo
from accounts.models import UserContactInfo


@receiver(post_save, sender=ShippingInfo)
def sync_profile_address(sender, instance, **kwargs):
    """
    Sync shipping info with user's contact info when:
    - User is authenticated
    - User chooses to save as default address
    """
    if instance.is_default and instance.user:
        contact_info, created = UserContactInfo.objects.update_or_create(
            user=instance.user,
            is_default=True,
            defaults={
                "phone_number": instance.phone_number,
                "street_address1": instance.street_address1,
                "street_address2": instance.street_address2,
                "town_or_city": instance.town_or_city,
                "county": instance.county,
                "postcode": instance.postcode,
                "country": instance.country
            }
        )

        if created:
            UserContactInfo.objects.filter(
                user=instance.user,
                is_default=True
            ).exclude(pk=contact_info.pk).update(is_default=False)
