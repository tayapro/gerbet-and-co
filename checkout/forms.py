from django import forms
from .models import ShippingInfo


class ShippingInfoForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        label="First Name",
        help_text="Required for guest users"
    )
    last_name = forms.CharField(
        required=False,
        label="Last Name",
        help_text="Required for guest users"
    )
    email = forms.CharField(
        required=False,
        label="Email",
        help_text="Required for guest users"
    )

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

        # Remove name fields for authenticated users
        if user and user.is_authenticated:
            del self.fields["first_name"]
            del self.fields["last_name"]
            del self.fields["email"]
        else:
            # Require for guests
            self.fields["first_name"].required = True
            self.fields["last_name"].required = True
            self.fields["email"].required = True

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.user:
            if not cleaned_data.get("first_name"):
                raise forms.ValidationError("First name is required for "
                                            "guest orders")
            if not cleaned_data.get("last_name"):
                raise forms.ValidationError("Last name is required for "
                                            "guest orders")
            if not cleaned_data.get("email"):
                raise forms.ValidationError("Email is required for "
                                            "guest orders")
        return cleaned_data

    class Meta:
        model = ShippingInfo
        fields = ["first_name", "last_name", "phone_number", "street_address1",
                  "street_address2", "town_or_city", "county",
                  "country", "postcode"]
