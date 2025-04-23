from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .bag import Bag
from products.models import Product


def add_to_bag(request, product_id):
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
    bag = Bag(request)
    bag.remove(product_id)
    return redirect("view_bag")


def update_bag(request, product_id):
    bag = Bag(request)
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get("action")
    quantity = request.POST.get("quantity")

    try:
        quantity = int(quantity)

        current_quantity = bag.get_quantity(product_id)
        result_quantity = current_quantity

        if action == "increase":
            result_quantity += 1
        elif action == "decrease":
            result_quantity -= 1
        else:
            result_quantity = quantity

        if result_quantity < 1 or result_quantity > 99:
            result_quantity = current_quantity

        bag.add(product_id,
                product_data={"title": product.title,
                              "price": product.price},
                quantity=result_quantity, action="update")
    except (ValueError, KeyError):
        pass

    updated_bag_quantity = bag.get_total_quantity()

    context = {"bag": bag,
               "bag_total_items": updated_bag_quantity,
               "product_name": product.title}

    if request.headers.get("HX-Request"):
        return render(request, "bag/htmx/update_bag.html", context)

    return redirect("view_bag")


def view_bag(request):
    bag = Bag(request)
    return render(request, "bag/view_bag.html", {"bag": bag})
