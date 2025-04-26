"""
URL configuration for gerbet_and_co project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

# Custom handler for Bad Request errors (400)
handler400 = 'gerbet_and_co.views.custom_400'
# Custom handler for Forbidden errors (403)
handler403 = 'gerbet_and_co.views.custom_403'
# Custom handler for Page Not Found errors (404)
handler404 = 'gerbet_and_co.views.custom_404'
# Custom handler for Server Error (500)
handler500 = 'gerbet_and_co.views.custom_500'
# CSRF-specific 403 error handler
handler403_csrf = 'gerbet_and_co.views.custom_403_csrf'

"""
URL configuration for the Gerbet & Co e-commerce platform.

Includes routes for:
- Store home and general pages
- User account management (registration, login, profile, addresses, orders)
- Django admin panel
- Product browsing and search
- Shopping bag management
- Checkout process with Stripe integration
- WYSIWYG editor (TinyMCE) for content management
- Serving sitemap.xml and robots.txt files
- Serving media files during development
"""

urlpatterns = [
    path("", include("store.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("products/", include("products.urls")),
    path("bag/", include("bag.urls")),
    path("checkout/", include("checkout.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("sitemap.xml", views.sitemap_view, name="sitemap"),
    path("robots.txt", views.robots_view, name="robots"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
