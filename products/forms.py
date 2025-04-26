from django import forms
import logging

from checkout.models import OrderItem
from .models import Product, Rating, RATING_CHOICES

logger = logging.getLogger(__name__)


class RatingForm(forms.ModelForm):
    """
    A form for submitting product ratings.

    Validates that the user has purchased the product before allowing
    rating submission. Also ensures that a rating value is selected.
    """

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label="Your Rating"
    )

    class Meta:
        model = Rating
        fields = ['rating']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, optionally associating it with a specific product.
        RatingForm requires an product to be passed
        when the form is initialized.
        """

        # Get 'product' from kwargs if provided.
        self.event = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        user = self.initial.get("user")
        product = cleaned_data.get("product")

        if user and product:
            has_purchased = OrderItem.objects.filter(
                order__user=user,
                product=product
            ).exists()
            if not has_purchased:
                raise forms.ValidationError("You can only rate "
                                            "products you've purchased.")

        rating = self.cleaned_data.get('rating')

        # Ensure the rating is provided
        if not rating:
            raise forms.ValidationError("Please select a rating.")

        return cleaned_data


class ProductAdminForm(forms.ModelForm):
    """
    A custom form used in the Django admin for managing Product instances.

    Allows admins to update product details, view the current image URL,
    and optionally provide a new image URL.
    """

    image_url = forms.URLField(
        label="New Image URL",
        required=False,
        help_text="Provide a direct URL for the image."
    )
    current_image_url = forms.CharField(
        label="Current Image URL",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        help_text="This is the current image URL stored in the database."
    )

    class Meta:
        model = Product
        fields = ["title", "price", "categories", "current_image_url",
                  "image_url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["current_image_url"].initial = self.instance.image

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_image_url = self.cleaned_data.get("image_url")

        if new_image_url:
            instance.image = new_image_url

        if commit:
            instance.save()
        return instance
