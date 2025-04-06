from django.shortcuts import render
from .models import Faq


def home(request):
    return render(request, "store/home.html")


def about(request):
    return render(request, "store/about.html")


def help(request):
    return render(request, "store/help.html")


def help_page(request):
    faqs = Faq.objects.filter(section="taste-and-treats")
    return render(request, "store/help_base.html", {"faqs": faqs})


def help_section(request, section):
    faqs = Faq.objects.filter(section=section)
    context = {
        "faqs": faqs,
        "selected_section": section,
    }

    if request.headers.get("Hx-Request") == "true":
        return render(request, "store/includes/faq_list.html", context)
    else:
        return render(request, "store/help_base.html", context)
