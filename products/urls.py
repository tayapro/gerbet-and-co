from django.urls import path
from . import views

"""
URL configuration for product-related views.

Includes routes for displaying product lists, product details,
searching products, and submitting product ratings.
"""

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("<int:product_id>/", views.product_view, name="product_view"),
    path("search/", views.product_search, name="product_search"),
    path("rating/<int:product_id>/", views.product_rating,
         name="product_rating"),
]
