from django.shortcuts import render, redirect, get_object_or_404
from .bag import Bag
from products.models import Product


def add_to_bag(request, product_id):
    bag = Bag(request)
    product = get_object_or_404(Product, id=product_id)
    bag.add(product_id=product.id)
    # TODO: do not redirect to bag page
    return redirect("view_bag")


def remove_from_bag(request, product_id):
    bag = Bag(request)
    bag.remove(product_id)
    return redirect("view_bag")


def view_bag(request):
    bag = Bag(request)
    return render(request, "bag/view_bag.html", {"bag": bag})
