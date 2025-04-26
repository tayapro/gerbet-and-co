from django.urls import path
from . import views

"""
URL configuration for shopping bag-related views in the Gerbet & Co e-commerce
platform.

Includes routes for viewing the shopping bag, adding products, removing
products, and updating product quantities using HTMX for dynamic updates.
"""

urlpatterns = [
    path("", views.view_bag, name="view_bag"),
    path("bag/add/<int:product_id>/", views.add_to_bag, name="add_to_bag"),
    path("bag/remove/<int:product_id>/", views.remove_from_bag,
         name="remove_from_bag"),
    path("update/<int:product_id>/", views.update_bag, name="update_bag"),
]
