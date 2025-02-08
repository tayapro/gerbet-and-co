from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    # for sub-categories
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               blank=True, related_name='children')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True)
    image = models.ImageField(upload_to='macarons/', blank=True,
                              null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True,
                                 blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
