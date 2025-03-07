from django import forms
from .models import ShippingInfo, Order


class ShippingInfoForm(forms.ModelForm):
    use_default = forms.BooleanField(
        required=False,
        label="Use my default address",
        help_text="Check to use your saved default address"
    )

    save_as_default = forms.BooleanField(
        required=False,
        label="Save as default address",
        help_text="Save this address for future checkouts"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if not user or not user.is_authenticated:
            del self.fields["use_default"]
            del self.fields["save_as_default"]

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.user:
            if not cleaned_data.get("first_name"):
                raise forms.ValidationError("First name is required for "
                                            "guest orders")
            if not cleaned_data.get("last_name"):
                raise forms.ValidationError("Last name is required for "
                                            "guest orders")
        return cleaned_data

    class Meta:
        model = ShippingInfo
        fields = ["street_address1",
                  "street_address2", "town_or_city", "county",
                  "country", "postcode"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["email"]


class CheckoutForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.user:
            if not cleaned_data.get("email"):
                raise forms.ValidationError("Email is required "
                                            "for guest checkout")
        return cleaned_data
