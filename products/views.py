from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from .models import Category, Product


sort_options = [
    ("price_asc", "Price ascending"),
    ("price_desc", "Price descending"),
    ("popularity", "Recommendation"),
]


def product_list(request):
    # Optimize the query with prefetch_related for many-to-many (categories)
    products = (
        Product.objects.only("title", "price", "image", "rating")
        .prefetch_related("categories")
    )

    order_by = request.GET.get("order_by", "popularity")

    # Apply filters
    products, selected_filters = product_filter(request, products)

    # Apply sorting
    products = product_sort(products, order_by)

    # Remove duplicates
    products = products.distinct()

    context = {
        "products": products,
        "sort_options": sort_options,
        "categories": Category.objects.all(),
        "ratings": [5, 4, 3],
        "selected_filters": selected_filters,
        "current_sort": order_by,
        "selected_categories": request.GET.getlist("category"),
        "min_price": request.GET.get("min_price", ""),
        "max_price": request.GET.get("max_price", ""),
    }

    if request.headers.get("Hx-Request") == "true":
        return render(request, "products/includes/product_list_sort.html",
                      context)

    return render(request, "products/product_list.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'products/product_detail.html',
                  {'product': product})


def product_search(request):
    query = request.GET.get("search_query", "")
    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )

    order_by = request.GET.get("order_by", "popularity")

    # Apply filters
    products, selected_filters = product_filter(request, products)

    # Apply sorting
    products = product_sort(products, order_by)

    # Remove duplicates
    products = products.distinct()

    # http://127.0.0.1:8000/products/search/?search_query=tea
    # http://127.0.0.1:8000/products/?order_by=price_asc&min_price=&max_price=

    context = {
        "products": products,
        "query": query,
        "order_by": order_by,
        "results_count": products.count(),
        "categories": Category.objects.all(),
        "ratings": [5, 4, 3],

        "selected_filters": selected_filters,
        "selected_categories": request.GET.getlist("category"),
        "min_price": request.GET.get("min_price", ""),
        "max_price": request.GET.get("max_price", ""),
    }

    if request.headers.get("Hx-Request") == "true":
        return render(request, "products/includes/product_list_sort.html",
                      context)

    return render(request, "products/product_search.html", context)


# Helper views
def product_filter(request, products):
    selected_filters = []

    # Filter by category
    category_slugs = request.GET.getlist("category")
    if category_slugs:
        products = products.filter(categories__slug__in=category_slugs)
        for slug in category_slugs:
            try:
                category = Category.objects.get(slug=slug)
                new_query = request.GET.copy()
                category_values = new_query.getlist("category")
                category_values.remove(slug)
                if category_values:
                    new_query.setlist("category", category_values)
                else:
                    new_query.pop("category", None)
                label = f"{category.name}"
                url = f"?{new_query.urlencode()}"
                selected_filters.append((label, url))
            except Category.DoesNotExist:
                continue

    # Filter by rating
    min_rating = request.GET.get("min_rating")
    if min_rating:
        products = products.filter(rating__gte=min_rating)
        new_query = request.GET.copy()
        new_query.pop("min_rating", None)
        selected_filters.append((f"{min_rating}+ stars",
                                 f"?{new_query.urlencode()}"))

    # Filter by price
    min_price = request.GET.get("min_price", "").strip()
    if min_price:
        try:
            products = products.filter(price__gte=min_price)
            new_query = request.GET.copy()
            new_query.pop("min_price", None)
            selected_filters.append((f"Min €{min_price}",
                                    f"?{new_query.urlencode()}"))
        except ValueError:
            pass

    max_price = request.GET.get("max_price")
    if max_price:
        products = products.filter(price__lte=max_price)
        new_query = request.GET.copy()
        new_query.pop("max_price", None)
        selected_filters.append((f"Max €{max_price}",
                                 f"?{new_query.urlencode()}"))

    return products, selected_filters


def product_sort(products, order_by):
    if order_by == "price_asc":
        products = products.order_by("price")
    elif order_by == "price_desc":
        products = products.order_by("-price")
    elif order_by == "popularity":
        products = products.order_by("-rating")

    return products
