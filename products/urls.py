from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
    path("search/", views.product_search, name="product_search"),
    path("sort/", views.product_list_sort, name="product_list_sort"),
]
