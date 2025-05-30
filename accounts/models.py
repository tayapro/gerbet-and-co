from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.db import models


class UserContactInfo(models.Model):
    """
    Represents a user's contact and address information for order-related
    communication.

    Includes fields for phone number, address details, and country selection.
    Allows users to store multiple addresses and mark one as the default.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    street_address1 = models.CharField(max_length=80, null=True, blank=True)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label="Select Country", max_length=2,
                           null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
