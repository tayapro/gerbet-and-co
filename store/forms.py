from django import forms

from .models import ContactMessage, Subscriber


class ContactForm(forms.ModelForm):
    """
    A form for users to submit inquiries via the Contact Us page.

    This form maps to the ContactMessage model and includes custom
    placeholders, validation, and user-friendly error messages for name,
    email, and message fields.
    """

    name = forms.CharField(
        max_length=100,
        label="Name",
        required=True,
        widget=forms.TextInput(attrs={
            "id": "id_name"
        }),
        error_messages={"required": "Please enter your email address."})
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "id": "id_email"
        }),
        error_messages={"required": "Please enter your email address."})
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "id": "id_message"}),
        label="Message",
        required=True,
        error_messages={"required": "Please enter your message."})

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "name": "Enter your name",
            "email": "Enter your email",
            "message": "Enter your message",
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
        contactMessage = super().save(commit=False)
        contactMessage.name = self.cleaned_data["name"]
        contactMessage.email = self.cleaned_data["email"]
        contactMessage.message = self.cleaned_data["message"]

        if commit:
            contactMessage.save()

        return contactMessage


class SubscribeForm(forms.ModelForm):
    """
    A simple form for subscribing users to the newsletter.

    Maps to the Subscriber model and handles the submission of user
    email addresses.
    """

    class Meta:
        model = Subscriber
        fields = ["email"]
