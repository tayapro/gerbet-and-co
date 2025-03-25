from django.contrib import admin
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "stock", "show_categories", "created_at")
    search_fields = ("title", "categories")
    filter_horizontal = ('categories',)
    ordering = ("title",)

    def show_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    show_categories.short_description = "categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
