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

    if action in ["increase", "decrease"]:
        bag.add(product_id, quantity=1, action=action)

    return redirect("view_bag")


def view_bag(request):
    bag = Bag(request)
    return render(request, "bag/view_bag.html", {"bag": bag})
