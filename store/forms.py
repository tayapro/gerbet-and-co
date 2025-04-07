from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        label="Name",
        required=True,
        error_messages={"required": "Please enter your email address."})
    email = forms.EmailField(
        label="Email",
        required=True,
        error_messages={"required": "Please enter your email address."})
    message = forms.CharField(
        widget=forms.Textarea,
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
