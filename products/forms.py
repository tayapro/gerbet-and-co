from django import forms
from .models import Rating, RATING_CHOICES
from checkout.models import OrderItem


class RatingForm(forms.ModelForm):
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
