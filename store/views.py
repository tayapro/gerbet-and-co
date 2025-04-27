from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render

from .forms import ContactForm, SubscribeForm
from .models import ContactMessage, Faq
from products.models import Product
from .utils import send_contact_us_email, send_subscription_email


def home(request):
    """
    Render the homepage with a list of featured products.
    """

    featured_products = Product.objects.filter(featured_badge__isnull=False)

    return render(request, "store/home_page.html", {
        "featured_products": featured_products})


def subscribe(request):
    """
    Handle newsletter subscription form submission.

    If successful, saves the subscriber's email and sends a confirmation email.
    Supports rendering success or error messages.
    """

    next = request.GET.get("next", "/")

    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data["email"]
                form.save()

                send_subscription_email(request, email)

                messages.success(request, "Thanks for subscribing!")
                return render(request, "store/home-page.html",
                              {"form": form, "next": next})
            except IntegrityError:
                messages.warning(request, "This email is already subscribed.")
            except Exception as e:
                messages.error(request, str(e))
        else:
            return render(request, "store/home_page.html",
                          {"form": form, "next": next,
                           "scroll_to": "newsletter-section-id"})

    form = SubscribeForm()
    return render(request, "store/home_page.html", {"form": form, "next": next,
                  "scroll_to": "newsletter-section-id"})


def info_page(request):
    """
    Render the information page with store policies and general info.
    """

    return render(request, "store/info_page.html")


def about_page(request):
    """
    Render the About page describing Gerbet & Co's story and values.
    """

    return render(request, "store/about_page.html")


def help_page(request):
    """
    Render the Help page with FAQs related to the Taste & Treats section.
    """

    faqs = Faq.objects.filter(section="taste-and-treats")
    return render(request, "store/help_page.html", {"faqs": faqs})


def help_section(request, section):
    """
    Dynamically load FAQ entries for a selected section.

    If the request is made via HTMX, returns only the FAQ list partial;
    otherwise, renders the full Help page.
    """

    faqs = Faq.objects.filter(section=section)
    context = {
        "faqs": faqs,
        "selected_section": section,
    }

    if request.headers.get("Hx-Request") == "true":
        return render(request, "store/includes/faq_list.html", context)
    else:
        return render(request, "store/help_page.html", context)


def contact_us_page(request):
    """
    Handle the Contact Us form submission.

    Saves the message to the database and sends a confirmation email to staff.
    Displays success or error messages to the user.
    """

    next = request.GET.get("next", "/")

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            try:
                ContactMessage.objects.create(
                    name=name,
                    email=email,
                    message=message
                )

                context = {"name": name, "email": email, "message": message}
                send_contact_us_email(request, context)
                messages.success(request, "Thanks for reaching out! "
                                 "We'll get back to you soon.")
            except Exception as e:
                messages.warning(request, f"Error: {e}")

            return redirect("home")
    else:
        form = ContactForm()

    return render(request, "store/contact_us_page.html",
                  {"form": form, "next": next})
