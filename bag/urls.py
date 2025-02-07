from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_bag, name="view_bag"),
    path("bag/add/<int:product_id>/", views.add_to_bag, name="add_to_bag"),
    path("bag/remove/<int:product_id>/", views.remove_from_bag,
         name="remove_from_bag"),
]
