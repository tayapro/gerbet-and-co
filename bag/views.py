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
        "image_url": product.image.url if product.image else "",
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

        if quantity < 1:
            quantity = 1
        elif quantity > 99:
            quantity = 99

        if action == "increase":
            bag.add(product_id,
                    product_data={"title": product.title,
                                  "price": product.price},
                    quantity=1, action="increase")
        elif action == "decrease":
            if bag.bag[str(product_id)]["quantity"] > 1:
                bag.add(product_id,
                        product_data={"title": product.title,
                                      "price": product.price},
                        quantity=-1, action="decrease")
        else:
            bag.add(product_id,
                    product_data={"title": product.title,
                                  "price": product.price},
                    quantity=quantity, action="update")

    except (ValueError, KeyError):
        pass

    updated_bag_quantity = bag.get_total_quantity()

    if request.headers.get("HX-Request"):
        return render(request, "bag/htmx/update_bag.html",
                      {"bag": bag, "bag_total_items": updated_bag_quantity,
                       "product_name": product.title})

    return redirect("view_bag")


def view_bag(request):
    bag = Bag(request)
    return render(request, "bag/view_bag.html", {"bag": bag})
