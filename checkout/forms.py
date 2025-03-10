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
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user and self.user.is_authenticated:
            instance.user = self.user
            instance.is_default = self.cleaned_data.get("save_as_default",
                                                        False)

        if commit:
            instance.save()

        # Handle guest data separately
        if not self.user.is_authenticated:
            Order.objects.filter(pk=instance.order.pk).update(
                guest_first_name=self.cleaned_data["guest_first_name"],
                guest_last_name=self.cleaned_data["guest_last_name"],
                guest_email=self.cleaned_data["guest_email"]
            )

        return instance

    class Meta:
        model = ShippingInfo
        fields = ["guest_first_name", "guest_last_name", "phone_number",
                  "street_address1", "street_address2", "town_or_city",
                  "county", "country", "postcode"]
