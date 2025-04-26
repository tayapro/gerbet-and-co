from django.contrib import admin
from tinymce.widgets import TinyMCE

from .forms import ProductAdminForm
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Product model.

    Features:
    - Custom form for managing product fields including image updates.
    - TinyMCE widget integration for rich text editing of product descriptions.
    - Searchable by title, description, and category name.
    - Allows horizontal filter selection for categories.
    """

    form = ProductAdminForm
    list_display = ("title", "description", "price", "show_categories",
                    "created_at")
    fields = ("title", "description", "price", "categories",
              "current_image_url", "image_url")
    search_fields = ("title", "description", "categories__name")
    filter_horizontal = ("categories",)
    ordering = ("title",)

    formfield_overrides = {
        Product.description: {
            'widget': TinyMCE(attrs={'cols': 80, 'rows': 20})
        },
    }

    def show_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    show_categories.short_description = "categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Category model.

    Features:
    - Auto-populates slug field based on the category name.
    - Enables search and ordering by category name.
    """

    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
