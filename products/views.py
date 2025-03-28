from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    products = Product.objects.all()

    return render(request, 'products/product_list.html',
                  {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'products/product_detail.html',
                  {'product': product})


def product_search(request):
    query = request.GET.get("search_query", "")
    order_by = request.GET.get("order_by", "popularity")
    print(f"ORDER_BY: {order_by}")

    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )
    print(f"PRODUCTS: {products}")

    if order_by == "price_asc":
        products = products.order_by("price")
    elif order_by == "price_desc":
        products = products.order_by("-price")
    elif order_by == "popularity":
        products = products.order_by("-rating")

    context = {
        "products": products,
        "query": query,
        "order_by": order_by,
        "results_count": products.count()
    }

    if request.htmx:
        return render(request, "products/includes/product_list_sort.html",
                      context)

    return render(request, "products/product_search.html", context)


def product_list_sort(request):
    order_by = request.GET.get("order_by", "popularity")
    products = Product.objects.all()

    if order_by == "price_asc":
        products = products.order_by("price")
    elif order_by == "price_desc":
        products = products.order_by("-price")
    elif order_by == "popularity":
        products = products.order_by("-rating")

    return render(request, "products/product_cards.html", {
        "products": products
    })
