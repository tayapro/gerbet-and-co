from django.contrib import admin
from tinymce.widgets import TinyMCE

from .forms import ProductAdminForm
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
