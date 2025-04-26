from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404

from .forms import RatingForm
from .models import Category, Product, Rating
from checkout.models import OrderItem

# Sort options available for the product list and search pages
sort_options = [
    ("price_asc", "Price (Low to High)"),
    ("price_desc", "Price (High to Low)"),
    ("popularity", "Popularity"),
]


def product_list(request):
    """
    Display a list of products with optional filtering and sorting.

    Supports category, rating, and price filters.
    Sort options include price and popularity.
    Adds dynamic star rating visualization to each product.
    """

    # Randomly shuffle the queryset
    products = Product.objects.order_by('?')

    # Apply filters
    products, selected_filters = product_filter(request, products)

    # Apply sorting
    order_by = request.GET.get("order_by", "")
    products, selected_sort = product_sort(request, products, order_by)

    # Remove duplicates
    products = products.distinct()

    # Add star fills
    for product in products:
        product.star_fills = get_star_fill_levels(product.rating or 0)

    # Combine filters and sort selection
    if selected_sort:
        selected_filters.append(selected_sort)

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
    """
    Display details for a specific product.

    Shows title, description, price, average rating, and allows
    authenticated users who purchased the product to leave a rating.
    """

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
        "can_rate": can_rate,
        "next": next
    }

    return render(request, "products/product_view.html", context)


def product_search(request):
    """
    Display search results for products based on user query.

    Supports the same filtering and sorting as the main product list.
    Shows a message if no search query is entered.
    """

    query = request.GET.get("search_query", "")
    if not query:
        messages.error(request, "Please enter a search term.")

    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )

    order_by = request.GET.get("order_by", "")

    # Apply filters
    products, selected_filters = product_filter(request, products)

    # Apply sorting
    products, selected_sort = product_sort(request, products, order_by)

    # Remove duplicates
    products = products.distinct()

    # Add star fills
    for product in products:
        product.star_fills = get_star_fill_levels(product.rating or 0)

    # Combine filters and sort selection
    if selected_sort:
        selected_filters.append(selected_sort)

    context = {
        "products": products,
        "sort_options": sort_options,
        "query": query,
        "order_by": order_by,
        "results_count": products.count(),
        "categories": Category.objects.all(),
        "ratings": [5, 4, 3],
        "selected_filters": selected_filters,
        "current_sort": order_by,
        "selected_categories": request.GET.getlist("category"),
        "min_price": request.GET.get("min_price", ""),
        "max_price": request.GET.get("max_price", ""),
    }

    return render(request, "products/product_search.html", context)


@login_required
def product_rating(request, product_id):
    """
    Allow authenticated users to rate a product they have purchased.

    Only users who previously bought the product can submit or update a rating.
    Updates the product's average rating after a new rating is saved.
    """

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
    Calculate star fill levels for rating visualization.

    Returns a list of 5 values (between 0.0 and 1.0) representing
    how much each star should be filled based on the rating.
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
    """
    Filter products based on query parameters.

    Supports filtering by:
    - Categories
    - Minimum star rating
    - Minimum and maximum price

    Returns the filtered queryset and a list of selected filters
    for displaying active filters in the UI.
    """

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


def product_sort(request, products, order_by):
    """
    Sort products based on the user's selected sorting option.

    Supports sorting by:
    - Price ascending
    - Price descending
    - Popularity (rating)

    Returns the sorted queryset and the selected sort option
    for UI display.
    """

    selected_sort = None

    # Apply sorting
    if order_by == "price_asc":
        products = products.order_by("price")
    elif order_by == "price_desc":
        products = products.order_by("-price")
    elif order_by == "popularity":
        products = products.order_by("-rating")

    # Map value to label using sort_options
    sort_dict = dict(sort_options)
    label = sort_dict.get(order_by)

    if label:
        new_query = request.GET.copy()
        new_query.pop("order_by", None)
        url = f"?{new_query.urlencode()}"
        selected_sort = (label, url)

    return products, selected_sort
