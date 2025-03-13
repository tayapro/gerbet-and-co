from django import forms
from .models import Order, ShippingInfo


class ShippingInfoForm(forms.ModelForm):
    guest_first_name = forms.CharField(
        required=False,
        label="First Name",
        help_text="Required for guest users"
    )
    guest_last_name = forms.CharField(
        required=False,
        label="Last Name",
        help_text="Required for guest users"
    )
    guest_email = forms.CharField(
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
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Remove name fields for authenticated users
        if self.user and self.user.is_authenticated:
            del self.fields["guest_first_name"]
            del self.fields["guest_last_name"]
            del self.fields["guest_email"]
        else:
            # Require for guests
            self.fields["guest_first_name"].required = True
            self.fields["guest_last_name"].required = True
            self.fields["guest_email"].required = True
            # Remove fields irrelevant for guest users
            del self.fields["save_as_default"]
            del self.fields["use_default"]

        # Define the exact order of fields
        field_order = [
            "use_default",  # Only present for authenticated users
            "guest_first_name",  # Only present for guests
            "guest_last_name",
            "guest_email",
            "phone_number",
            "street_address1",
            "street_address2",
            "town_or_city",
            "county",
            "postcode",
            "country",
            "save_as_default"
        ]

        self.fields = {
            key: self.fields[key]
            for key in field_order
            if key in self.fields
        }

    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not self.user.is_authenticated:
            if not cleaned_data.get("guest_first_name"):
                raise forms.ValidationError("First name is required for "
                                            "guest orders")
            if not cleaned_data.get("guest_last_name"):
                raise forms.ValidationError("Last name is required for "
                                            "guest orders")
            if not cleaned_data.get("guest_email"):
                raise forms.ValidationError("Email is required for "
                                            "guest orders")

        # Validate address fields for authenticated users
        # if "use_default" is not checked
        if (
            self.user
            and self.user.is_authenticated
            and not cleaned_data.get("use_default")
        ):
            required_fields = [
                "phone_number",
                "street_address1",
                "town_or_city",
                "country"
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    raise forms.ValidationError(
                        field, f"{self.fields[field].label} is required."
                    )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user and self.user.is_authenticated:
            instance.user = self.user
            if self.cleaned_data.get("save_as_default", False):
                instance.is_default = True

        # Handle guest data separately
        if self.user is None:
            Order.objects.filter(pk=instance.order.pk).update(
                guest_first_name=self.cleaned_data["guest_first_name"],
                guest_last_name=self.cleaned_data["guest_last_name"],
                guest_email=self.cleaned_data["guest_email"]
            )

        if commit:
            instance.save()

        return instance

    class Meta:
        model = ShippingInfo
        fields = ["guest_first_name", "guest_last_name", "guest_email",
                  "phone_number", "street_address1", "street_address2",
                  "town_or_city", "county", "country", "postcode"]
