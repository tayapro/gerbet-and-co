from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import CustomUserCreationForm
from .utils import send_welcome_email


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                messages.error(request,
                               "Account with this email already exists.")
                return render(request, "accounts/register.html",
                              {"form": form})

            user = form.save()
            auth_login(request, user,
                       backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Account created successfully!")

            try:
                send_welcome_email(request, user)
            except Exception:
                messages.warning(request,
                                 "Account created, but welcome email failed to send.")

            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            remember_me = request.POST.get('remember_me')
            if remember_me:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(0)

            messages.success(request, "Successfully logged in!")
            return redirect("product_list")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout(request):
    next = request.POST.get("next", reverse("home"))

    if not request.user.is_authenticated:
        return redirect(next)

    if request.method == "POST":
        auth_logout(request)
        messages.success(request, "You have been logged out!")
        return redirect(next)

    return render(request, "accounts/logout.html", {"next": next})
