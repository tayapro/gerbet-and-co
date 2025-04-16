from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify


class Category(models.Model):
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
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField()
    categories = models.ManyToManyField("Category", related_name="products")
    image = CloudinaryField("image", folder=settings.CLOUDINARY_UPLOAD_FOLDER,
                            resource_type="auto", blank=True)
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
    Represents a user's rating for a product.
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
