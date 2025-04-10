"""
URL configuration for gerbet_and_co project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("store.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("products/", include("products.urls")),
    path("bag/", include("bag.urls")),
    path("checkout/", include("checkout.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
