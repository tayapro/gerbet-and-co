from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from decimal import Decimal

from .models import Category, Product


def product_list(request):
    products = Product.objects.all()
    selected_filters = []

    # Category filter
    category_slugs = request.GET.getlist("category")
    if category_slugs:
        products = products.filter(categories__slug__in=category_slugs)
        for slug in category_slugs:
            try:
                category = Category.objects.get(slug=slug)
                # Build query excluding this category
                new_query = request.GET.copy()
                category_values = new_query.getlist("category")
                category_values.remove(slug)
                if category_values:
                    new_query.setlist("category", category_values)
                else:
                    new_query.pop("category", None)

                label = f"Category: {category.name}"
                url = f"?{new_query.urlencode()}"
                selected_filters.append((label, url))
            except Category.DoesNotExist:
                continue

    # Rating filter
    min_rating = request.GET.get("min_rating")
    if min_rating:
        products = products.filter(rating__gte=min_rating)
        selected_filters.append((f"{min_rating}+ stars", "min_rating",
                                 min_rating))

    # Price range
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
        selected_filters.append((f"Min €{min_price}", "min_price", min_price))
    if max_price:
        products = products.filter(price__lte=max_price)
        selected_filters.append((f"Max €{max_price}", "max_price", max_price))

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "ratings": [5, 4, 3],
        "selected_filters": selected_filters,
    }

    if request.headers.get("Hx-Request") == "true":
        print(f"SELECTED FILTERS: {selected_filters}")
        return render(request, "products/includes/product_list_sort.html",
                      context)

    return render(request, "products/product_list.html", context)


def product_list_old(request):
    products = Product.objects.all()

    # Filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    categories = request.GET.getlist("category")
    print(f"CATEGORIES: {categories}")

    if categories:
        products = products.filter(categories__slug__in=categories)

    min_rating = request.GET.get("min_rating")
    print(f"MIN RATING: {min_rating}")

    if min_rating:
        products = products.filter(rating__gte=min_rating)

    context = {
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "categories": Category.objects.all(),
        "ratings": [5, 4, 3, 2, 1],
    }

    if request.headers.get("Hx-Request") == "true":
        return render(request, "products/includes/product_list_sort.html",
                      context)

    return render(request, 'products/product_list.html', context)


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
