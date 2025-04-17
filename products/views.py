from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404

from .forms import RatingForm
from .models import Category, Product, Rating
from checkout.models import OrderItem

sort_options = [
    ("price_asc", "Price ascending"),
    ("price_desc", "Price descending"),
    ("popularity", "Recommendation"),
]


def product_list(request):
    products = Product.objects.all()
    order_by = request.GET.get("order_by", "popularity")

    # Apply filters
    products, selected_filters = product_filter(request, products)
    print(f"SELECTED_FILTERS: {selected_filters}")

    # Apply sorting
    products = product_sort(products, order_by)

    # Remove duplicates
    products = products.distinct()

    for product in products:
        product.star_fills = get_star_fill_levels(product.rating or 0)

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

    return render(request, "products/product_list.html", context)


def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    can_rate = False
    if request.user.is_authenticated:
        can_rate = product.purchased_by(request.user)

    rating_form = RatingForm()
    star_fills = get_star_fill_levels(product.rating or 0)

    context = {
        "product": product,
        "rating_form": rating_form,
        "star_fills": star_fills,
        "can_rate": can_rate
    }

    return render(request, "products/product_view.html", context)


def product_search(request):
    query = request.GET.get("search_query", "")
    if not query:
        messages.error(request, "Please enter a search term.")

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

    return render(request, "products/product_search.html", context)


@login_required
def product_rating(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Only allow rating if user purchased the product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()

    if not has_purchased:
        messages.error(request, "You can only rate products you've purchased.")
        return redirect("product_view", product_id=product.id)

    if request.method == "POST":
        form = RatingForm(request.POST, product=product)

        if form.is_valid():
            Rating.objects.filter(user=request.user, product=product).delete()

            rating = form.save(commit=False)
            rating.user = request.user
            rating.product = product
            rating.save()

            average = product.get_average_rating()
            if average is not None:
                product.rating = average
                product.save(update_fields=["rating"])

            messages.success(request, "Your rating has been submitted.")
        else:
            messages.error(request, "Invalid rating. Please try again.")

    return redirect("product_view", product_id=product.id)


# Helper views
def get_star_fill_levels(rating):
    """
    Returns a list of 5 fill values (0.0 to 1.0) per star based on rating.
    Example: 4.3 → [1, 1, 1, 1, 0.3]
    """
    fill_levels = []
    for i in range(1, 6):
        if rating >= i:
            fill_levels.append(1)
        elif rating > i - 1:
            fill_levels.append(round(rating - (i - 1), 2))
        else:
            fill_levels.append(0)
    return fill_levels


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
            selected_filters.append((
                f"Min €{float(min_price):.2f}",
                f"?{new_query.urlencode()}"
            ))
        except ValueError:
            pass

    max_price = request.GET.get("max_price")
    if max_price:
        products = products.filter(price__lte=max_price)
        new_query = request.GET.copy()
        new_query.pop("max_price", None)
        selected_filters.append((
            f"Max €{float(max_price):.2f}",
            f"?{new_query.urlencode()}"
        ))

    return products, selected_filters


def product_sort(products, order_by):
    if order_by == "price_asc":
        products = products.order_by("price")
    elif order_by == "price_desc":
        products = products.order_by("-price")
    elif order_by == "popularity":
        products = products.order_by("-rating")

    return products
