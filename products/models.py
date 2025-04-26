from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.uploader import destroy
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from tinymce.models import HTMLField


class Category(models.Model):
    """
    Represents a category for organizing products.
    Supports hierarchical categories through the optional parent field.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    # for sub-categories
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True,
                               blank=True, related_name="children")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


FEATURED_BADGES = [
    ("spring", "Spring Special"),
    ("bestseller", "Bestseller"),
    ("new", "New Arrival"),
]


class Product(models.Model):
    """
    Represents a product with attributes such as title, description, price,
    image, rating, and category associations. Includes logic for slug
    generation, image deletion, and checking if a user purchased the product.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = HTMLField()
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    categories = models.ManyToManyField("Category", related_name="products")
    image = models.URLField("Image URL", max_length=500, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True,
                                 blank=True)
    featured_badge = models.CharField(
                    max_length=20,
                    choices=FEATURED_BADGES,
                    blank=True,
                    null=True,
                    help_text="Optional badge for featured products"
                )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        """
        Metadata for the Products model.
        """
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        try:
            if not self.slug:
                self.slug = slugify(self.title)
            super().save(*args, **kwargs)

        except CloudinaryError:
            raise ValidationError("Image upload failed. Please check your " +
                                  "connection or try again later.")
        except Exception as e:
            raise ValidationError(f"Unexpected error during save: {e}")

    def delete(self, *args, **kwargs):
        """
        Override the delete method to handle Cloudinary image deletion.
        Ensures graceful handling of errors during the image removal process.
        """
        try:
            # Remove the associated image from Cloudinary if it exists
            if self.image:
                public_id = self.image.public_id
                # Destroy is a Cloudinary-specific method
                destroy(public_id, invalidate=True)
        except CloudinaryError:
            raise ValidationError("Failed to delete image from Cloudinary. " +
                                  "Please check your connection or try again" +
                                  " later.")

    def get_average_rating(self):
        avg = self.ratings.aggregate(Avg("rating"))["rating__avg"]
        if avg is not None:
            return round(avg, 1)
        return None

    def purchased_by(self, user):
        from checkout.models import OrderItem
        return OrderItem.objects.filter(
            order__user=user,
            product=self
        ).exists()


RATING_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]


class Rating(models.Model):
    """
    Represents a user's rating for a product, allowing users to rate products
    from 1 to 5 stars. Supports ordering by creation date and indexing
    for efficient queries.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="product_ratings")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name="ratings")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Rating: {self.rating} stars by {self.user} "
            f"for {self.product.title}"
        )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]
        verbose_name = "Rating"
