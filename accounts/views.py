from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetConfirmView)
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from .forms import (
    CustomUserCreationForm, CustomPasswordChangeForm,
    ProfileUpdateForm, UserContactInfoUpdateForm)
from .models import UserContactInfo
from checkout.models import Order
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
                                 "Account created, but welcome email "
                                 "failed to send.")

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

            messages.success(request, "Successfully logged in.")
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
        messages.success(request, "You have been logged out.")
        return redirect(next)

    return render(request, "accounts/logout.html", {"next": next})


@login_required
def account(request):
    next = request.GET.get("next", "/")

    user = request.user
    orders = Order.objects.filter(user=user)
    addresses = UserContactInfo.objects.filter(user=user)

    context = {
        "user": user,
        "orders": orders,
        "addresses": addresses,
        "next": next,
    }
    return render(request, "accounts/account.html", context)


@login_required
def profile_view(request):
    return render(request, "accounts/htmx/profile_view.html",
                  {"user": request.user})


@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            context = {
                "user": request.user,
                "toast_message": "Your profile has been successfully changed.",
            }
            return render(request,
                          "accounts/htmx/profile_view.html",
                          context)
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request,
                  "accounts/htmx/profile_update.html",
                  {"form": form})


@login_required
def address_create(request):
    if request.method == "POST":
        form = UserContactInfoUpdateForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect("account")
    else:
        form = UserContactInfoUpdateForm()

    context = {
        "form": form
    }
    return render(request, "accounts/address_create.html", context)


@login_required
def address_view(request):
    addresses = UserContactInfo.objects.filter(user=request.user)

    return render(request, "accounts/address_view.html",
                  {"addresses": addresses})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_update.html"
    form_class = CustomPasswordChangeForm

    def form_valid(self, form):
        form.save()
        # Redirect to the login page with a success message
        return redirect(reverse_lazy("login") + "?password_change=success")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        form.save()

        # Redirect to the login page with a success message
        return redirect(reverse_lazy("login") + "?password_reset=success")
