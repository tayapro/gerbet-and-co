from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("help/", views.help_page, name="help"),
    path("help/section/<str:section>/", views.help_section,
         name="help_section"),
    path("contact-us/", views.contact_us_page, name="contact_us")
]
