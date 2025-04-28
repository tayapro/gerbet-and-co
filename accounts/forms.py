from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm, PasswordResetForm,
    UserCreationForm
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import re

from .models import UserContactInfo


def validate_phone(value):
    """Validate phone number format: Allows + and 7-15 digits."""
    phone_regex = re.compile(r"^\+?\d{7,15}$")
    if not phone_regex.match(value):
        raise ValidationError("Enter a valid phone number (7-15 digits, "
                              "optional '+').")


class UserRegistrationForm(UserCreationForm):
    """
    A form for user registration, extending Django's UserCreationForm.

    Adds custom validations for username, email, and first/last name fields.
    Also customizes placeholders for a smoother user experience.
    """

    username = forms.CharField(validators=[MinLengthValidator(2)],
                               required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(validators=[MinLengthValidator(2)],
                                 required=True)
    last_name = forms.CharField(validators=[MinLengthValidator(2)],
                                required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "username": "Enter your username",
            "email": "Enter your email",
            "first_name": "First name",
            "last_name": "Last name",
            "password1": "Enter your password",
            "password2": "Enter your password again",
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs.update({
                "placeholder": placeholder,
                "class": "custom-placeholder"
            })

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    """
    A form for updating basic user profile details such as
    first name, last name, and (read-only) email address.

    Includes minimum length validation for names.
    """

    first_name = forms.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    last_name = forms.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data


class AddressForm(forms.ModelForm):
    """
    A form for creating and updating shipping addresses.

    Includes optional default address setting,
    phone number validation, and country selection widget.
    """

    street_address1 = forms.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    street_address2 = forms.CharField(
        required=False,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    town_or_city = forms.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    county = forms.CharField(
        required=False,
        widget=forms.TextInput(),
    )
    postcode = forms.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(),
    )
    country = CountryField(blank_label="Select country").formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            "class": "form-control",
            "data-placeholder": "Select your country"
        }),
    )
    phone_number = forms.CharField(
        required=True,
        validators=[validate_phone],
        widget=forms.TextInput(),
    )
    set_as_default = forms.BooleanField(
        required=False,
        label="Set as default shipping address",
        help_text="Checkout will use this address by default"
    )

    class Meta:
        model = UserContactInfo
        fields = [
            "street_address1", "street_address2",
            "town_or_city", "county", "postcode",
            "country", "phone_number", "set_as_default"
        ]


class CustomPasswordResetForm(PasswordResetForm):
    """
    A customized password reset form that verifies whethere
    the provided email is associated with an existing user.
    """

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with "
                                        "the specified email address.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    A customized password change form that prevents users
    from setting the same password as the old one.
    """

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if (
            old_password
            and (new_password1 == new_password2)
            and old_password == new_password1
        ):
            raise forms.ValidationError(
                "The new password cannot be the same as the old password.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "New password*"
        self.fields["new_password2"].label = "New password confirmation*"
