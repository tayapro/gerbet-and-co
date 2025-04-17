from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm, SubscribeForm
from .models import ContactMessage, Faq, Subscriber
from products.models import Product
from .utils import send_contact_us_email, send_subscription_email


def home(request):
    featured_products = Product.objects.filter(featured_badge__isnull=False)

    return render(request, "store/home.html", {
        "featured_products": featured_products})


def subscribe(request):
    next = request.GET.get("next", "/")

    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data["email"]
                form.save()

                # context = {"email": email}

                send_subscription_email(request, email)

                messages.success(request, "Thanks for subscribing!")
            except Exception as e:
                messages.error(e)
        else:
            return render(request, "store/home.html",
                          {"form": form, "next": next,
                           "scroll_to": "newsletter-section-id"})

    form = SubscribeForm()
    return render(request, "store/home.html", {"form": form, "next": next,
                  "scroll_to": "newsletter-section-id"})


def about_page(request):
    return render(request, "store/about_page.html")


def help_page(request):
    faqs = Faq.objects.filter(section="taste-and-treats")
    return render(request, "store/help_page.html", {"faqs": faqs})


def help_section(request, section):
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
