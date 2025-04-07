from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import ContactMessage, Faq


def home(request):
    return render(request, "store/home.html")


def about(request):
    return render(request, "store/about.html")


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
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            messages.success(request, "Thanks for reaching out! "
                             "We'll get back to you soon.")
            return redirect("contact_us")
    else:
        form = ContactForm()

    return render(request, "store/contact_us_page.html", {"form": form})
