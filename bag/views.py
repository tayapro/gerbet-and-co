from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .bag import Bag
from products.models import Product


def add_to_bag(request, product_id):
    bag = Bag(request)
    product = get_object_or_404(Product, id=product_id)

    product_data = {
        'title': product.title,
        'price': product.price,
        'image_url': product.image.url if product.image else '',
    }
    bag.add(product_id=product.id, product_data=product_data, quantity=1)

    next = request.GET.get("next", reverse("product_list"))

    return redirect(next)


def remove_from_bag(request, product_id):
    bag = Bag(request)
    bag.remove(product_id)
    return redirect("view_bag")


def update_bag(request, product_id):
    bag = Bag(request)
    action = request.POST.get("action")
    quantity = request.POST.get("quantity")

    try:
        quantity = int(quantity)

        if quantity < 1:
            quantity = 1
        elif quantity > 99:
            quantity = 99

        if action == "increase":
            bag.add(product_id, quantity=1, action="increase")
        if action == "decrease":
            bag.add(product_id, quantity=-1, action="decrease")
        if action == "update":
            bag.add(product_id, quantity=quantity, action="update")

    except ValueError:
        pass

    return redirect("view_bag")


def view_bag(request):
    bag = Bag(request)
    return render(request, "bag/view_bag.html", {"bag": bag})
