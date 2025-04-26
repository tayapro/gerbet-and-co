from django.urls import path

from . import views

"""
URL configuration for the Store app.

Includes routes for homepage, about page, help and FAQ sections,
contact form, subscription form, and information page.
"""

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about_page, name="about"),
    path("help/", views.help_page, name="help"),
    path("help/section/<str:section>/", views.help_section,
         name="help_section"),
    path("contact-us/", views.contact_us_page, name="contact_us"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("info/", views.info_page, name="info")
]
