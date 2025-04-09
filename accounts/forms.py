from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm, PasswordResetForm,
    UserCreationForm
)
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django_countries.widgets import CountrySelectWidget

from .models import UserContactInfo


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "username": "Enter your username",
            "email": "Enter your email",
            "first_name": "First name (optional)",
            "last_name": "Last name (optional)",
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
            first_name = cleaned_data.get("first_name")
            last_name = cleaned_data.get("last_name")
            email = cleaned_data.get("email")

            if not first_name:
                self.add_error("first_name", "First name cannot be empty")
            if not last_name:
                self.add_error("last_name", "Last name cannot be empty")
            if not email:
                self.add_error("email", "Email cannot be empty")

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
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")

        if not first_name:
            self.add_error("first_name", "First name cannot be empty")
        if not last_name:
            self.add_error("last_name", "Last name cannot be empty")
        if not email:
            self.add_error("email", "Email cannot be empty")

        return cleaned_data


class AddressForm(forms.ModelForm):
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

        widgets = {
            "country": CountrySelectWidget(attrs={
                "class": "form-control",
            })
        }


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with "
                                        "the specified email address.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
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
        self.fields['new_password1'].label = "New password*"
        self.fields['new_password2'].label = "New password confirmation*"
