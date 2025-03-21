from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, EmailValidator
import re

from .models import Order, ShippingInfo


def validate_phone_number(value):
    """Validate phone number format: Allows + and 7-15 digits."""
    phone_regex = re.compile(r"^\+?\d{7,15}$")
    if not phone_regex.match(value):
        raise ValidationError("Enter a valid phone number (7-15 digits, "
                              "optional '+').")


class ShippingInfoForm(forms.ModelForm):
    guest_first_name = forms.CharField(
        required=False,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    guest_last_name = forms.CharField(
        required=False,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    guest_email = forms.EmailField(
        required=False,
        validators=[EmailValidator()],
        widget=forms.EmailInput(),
    )
    phone_number = forms.CharField(
        required=True,
        validators=[validate_phone_number],
        widget=forms.TextInput(),
    )
    street_address1 = forms.CharField(
        required=True,
        validators=[MinLengthValidator(5)],
        widget=forms.TextInput(),
    )
    town_or_city = forms.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    postcode = forms.CharField(
        required=True,
        validators=[MinLengthValidator(4)],
        widget=forms.TextInput(),
    )
    country = CountryField(blank_label="Select country").formfield(
        widget=CountrySelectWidget(
            attrs={"class": "form-control",
                   "data-placeholder": "Select your country"}
        )
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

    def validate_required_fields(self, fields, data, errors):
        for field in fields:
            if not data.get(field):
                errors[field] = f"{self.fields[field].label} is required."

    def is_guest_user(self):
        return not self.user or not self.user.is_authenticated

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
        for field_name in ["guest_first_name",
                           "guest_last_name",
                           "street_address1",
                           "street_address2",
                           "town_or_city",
                           "county"]:
            self.fields[field_name].widget.attrs.update({"data-validate":
                                                         "text"})
        self.fields["phone_number"].widget.attrs.update({
            "data-validate": "tel"
        })
        self.fields["guest_email"].widget.attrs.update({
            "data-validate": "email"
        })
        self.fields["country"].widget.attrs.update({
            "data-validate": "select-one"
        })

    def clean(self):
        cleaned_data = super().clean()
        errors = {}

        # Validate guest users
        if self.is_guest_user():
            self.validate_required_fields(["guest_first_name",
                                           "guest_last_name",
                                           "guest_email"],
                                          cleaned_data, errors)

        # Validate address fields for authenticated users
        # if "use_default" is unchecked
        if (
            self.user
            and self.user.is_authenticated
            and not cleaned_data.get("use_default")
        ):
            self.validate_required_fields(["phone_number",
                                           "street_address1",
                                           "town_or_city", "country"],
                                          cleaned_data, errors)

        if errors:
            raise forms.ValidationError([(field, error) for field, error
                                         in errors.items()])

        return self.cleaned_data

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
