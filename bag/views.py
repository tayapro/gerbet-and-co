from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .bag import Bag
from products.models import Product


def add_to_bag(request, product_id):
    """
    Add a product to the bag or increase its quantity by one.

    Supports both standard and HTMX requests. Displays a toast
    notification on successful addition if HTMX is used.
    """

    bag = Bag(request)
    product = get_object_or_404(Product, id=product_id)

    product_data = {
        "title": product.title,
        "price": product.price,
        "image_url": product.image,
    }
    bag.add(product_id=product.id, product_data=product_data, quantity=1)

    updated_bag_quantity = bag.get_total_quantity()

    if request.headers.get("HX-Request"):
        return render(request, "bag/htmx/bag_toast.html",
                      {"product_name": product_data['title'],
                       "bag_total_items": updated_bag_quantity},
                      content_type="text/html")

    next = request.GET.get("next", reverse("product_list"))

    return redirect(next)


def remove_from_bag(request, product_id):
    """
    Remove a product from the bag.

    Redirects the user back to the bag view after removal.
    """

    bag = Bag(request)
    bag.remove(product_id)
    return redirect("view_bag")


def update_bag(request, product_id):
    """
    Update the quantity of a product in the bag.

    Supports 'increase', 'decrease', or direct quantity updates.
    Handles validation for quantity boundaries (1 - 99).
    Dynamically updates the bag using HTMX if available.
    """

    bag = Bag(request)
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get("action")
    quantity = request.POST.get("quantity")

    try:
        quantity = int(quantity)

        if action == "increase":
            quantity += 1
        elif action == "decrease":
            quantity -= 1

        # Handle invalid quantity
        if quantity < 1 or quantity > 99:
            updated_bag_quantity = bag.get_total_quantity()
            context = {
                "bag": bag,
                "bag_total_items": updated_bag_quantity,
                "product_name": product.title,
                "error": True,
            }

            if request.headers.get("HX-Request"):
                return render(request, "bag/htmx/update_bag.html", context)
            else:
                messages.error(request, "Invalid quantity selected.")
                return redirect("view_bag")

        # Valid quantity, update the bag
        bag.add(
            product_id,
            product_data={"title": product.title, "price": product.price},
            quantity=quantity,
            action="update",
        )

    except (ValueError, KeyError):
        pass

    updated_bag_quantity = bag.get_total_quantity()
    context = {
        "bag": bag,
        "bag_total_items": updated_bag_quantity,
        "product_name": product.title,
    }

    if request.headers.get("HX-Request"):
        return render(request, "bag/htmx/update_bag.html", context)

    return redirect("view_bag")


def view_bag(request):
    """
    Display the current contents of the user's shopping bag.
    """

    bag = Bag(request)
    return render(request, "bag/view_bag.html", {"bag": bag})
