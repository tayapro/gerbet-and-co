from django import forms
from .models import ShippingInfo, Order


class ShippingInfoForm(forms.ModelForm):
    class Meta:
        model = ShippingInfo
        fields = ["full_name", "phone_number", "street_address1",
                  "street_address2", "town_or_city", "county",
                  "country", "postcode"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["email"]
