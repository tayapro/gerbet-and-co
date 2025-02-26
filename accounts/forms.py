from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm, PasswordResetForm, UserCreationForm
)
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form that includes additional fields:
    email, first_name, and last_name.
    """
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
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "password1": "Enter your password",
            "password2": "Enter your password again",
        }

        for field, placeholder in placeholders.items():
            self.fields[field].widget.attrs.update({
                "placeholder": placeholder,
                "class": "custom-placeholder"
            })

    def save(self, commit=True):
        """Save user instance with cleaned data."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with "
                                        "the specified email address.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    User = get_user_model()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')

        if not first_name:
            self.add_error('first_name', 'First name cannot be empty')
        if not last_name:
            self.add_error('last_name', 'Last name cannot be empty')
        if not email:
            self.add_error('email', 'Email cannot be empty')

        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if (
            old_password
            and (new_password1 == new_password2)
            and old_password == new_password1
        ):
            raise forms.ValidationError(
                "The new password cannot be the same as the old password.")

        return cleaned_data
