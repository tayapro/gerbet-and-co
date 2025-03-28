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
    print(f"QUERY: {query}")
    results = []

    if query:
        results = Product.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()

    print(f"SEARCH QUERY RESULT: {results}")

    context = {
        "query": query,
        "results": results,
        "results_count": len(results)
    }
    return render(request, "products/search_results.html", context)
