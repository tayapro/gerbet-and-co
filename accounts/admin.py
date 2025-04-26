from django.contrib import admin
from .models import UserContactInfo


@admin.register(UserContactInfo)
class UserContactInfoAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserContactInfo model.

    Enables listing, filtering, searching, and ordering of user contact
    information in the Django admin panel for better management and review.
    """

    list_display = ("user", "phone_number", "street_address1", "town_or_city",
                    "postcode", "country")
    list_filter = ("country", "town_or_city")
    search_fields = ("user__username", "user__email", "phone_number",
                     "street_address1", "postcode")
    ordering = ("user",)
