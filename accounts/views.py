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
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy

from checkout.models import Order
from .constants import Tabs
from .forms import (
    UserRegistrationForm,
    CustomPasswordChangeForm,
    UserProfileForm,
    AddressForm)
from .models import UserContactInfo
from .utils import send_welcome_email


def register(request):
    next = request.GET.get("next", "/")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                messages.error(request,
                               "Account with this email already exists.")
                return render(request, "accounts/register.html",
                              {"form": form})

            user = form.save()

            try:
                send_welcome_email(request, user)
            except Exception:
                messages.warning(request,
                                 "Account created, but welcome email "
                                 "failed to send.")

            return redirect(reverse_lazy("login") + "?registration=success")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html",
                  {"form": form, "next": next})


def login(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    next = request.GET.get("next", "/")

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

    return render(request, "accounts/login.html", {"form": form, "next": next})


def logout(request):
    next = request.GET.get("next", "/")

    if not request.user.is_authenticated:
        return redirect(next)

    if request.method == "POST":
        auth_logout(request)
        messages.success(request, "You have been logged out.")
        return redirect(next)

    return render(request, "accounts/logout.html", {"next": next})


@login_required
def account_view(request):
    next = request.GET.get("next", "/")

    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    addresses = (
        UserContactInfo.objects
        .filter(user=user)
        .order_by('-is_default', '-updated_at')
    )

    tabs = [
        {
            'id': Tabs.RESIDENT_PROFILE,
            'label': 'Resident Profile',
            'template': 'accounts/includes/resident_profile.html',
            'is_default': True,
        },
        {
            'id': Tabs.ADDRESS_BOOK,
            'label': 'Address Book',
            'template': 'accounts/includes/address_book.html',
            'is_default': False,
        },
        {
            'id': Tabs.DELIVERY_AT_DOOR,
            'label': 'Deliveries at the Door',
            'template': 'accounts/includes/deliveries_at_the_door.html',
            'is_default': False,
        },
    ]

    context = {
        "user": user,
        "orders": orders,
        "addresses": addresses,
        "next": next,
        "tabs": tabs,
        "default_tab": Tabs.DEFAULT_TAB
    }
    return render(request, "accounts/account.html", context)


@login_required
def profile_view(request):
    return render(request, "accounts/htmx/profile_view.html",
                  {"user": request.user})


@login_required
def profile_update(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
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
        form = UserProfileForm(instance=request.user)

    return render(request,
                  "accounts/htmx/profile_update.html",
                  {"form": form})


@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if form.cleaned_data['set_as_default']:
                UserContactInfo.objects.filter(
                    user=request.user, is_default=True
                ).update(is_default=False)
                address.is_default = True
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect(f"{reverse('account')}?tab={Tabs.ADDRESS_BOOK}")
    else:
        form = AddressForm()

    context = {
        "form": form,
        "tab": Tabs.ADDRESS_BOOK,
    }
    return render(request, "accounts/address_form.html", context)


@login_required
def address_view(request):
    addresses = UserContactInfo.objects.filter(user=request.user)

    return render(request, "accounts/address_view.html",
                  {"addresses": addresses})


@login_required
def address_update(request, id):
    address = get_object_or_404(UserContactInfo, id=id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            if form.cleaned_data['set_as_default']:
                UserContactInfo.objects.filter(
                    user=request.user, is_default=True
                ).exclude(id=address.id).update(is_default=False)
                address.is_default = True
            else:
                address.is_default = False
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect(f"{reverse('account')}?tab={Tabs.ADDRESS_BOOK}")
    else:
        form = AddressForm(instance=address, initial={
            "set_as_default": address.is_default
        })

    context = {
        "form": form,
        "address": address,
        "tab": Tabs.ADDRESS_BOOK,
    }
    return render(request, "accounts/address_form.html", context)


@login_required
def address_delete(request, id):
    address = get_object_or_404(UserContactInfo, id=id, user=request.user)

    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect(f"{reverse('account')}?tab={Tabs.ADDRESS_BOOK}")

    context = {
        "address": address,
        "tab": Tabs.ADDRESS_BOOK,
    }
    return render(request, "accounts/address_delete.html", context)


@login_required
@require_POST
@transaction.atomic
def set_default_address(request, id):
    # Retrieve and reset all addresses for the user
    UserContactInfo.objects.filter(
        user=request.user, is_default=True
    ).update(is_default=False)

    # Set the selected address as the default
    address = get_object_or_404(UserContactInfo, id=id, user=request.user)
    address.is_default = True
    address.save()

    # Send success message and redirect
    messages.success(request, "Default shipping address updated")
    return redirect(f"{reverse('account')}?tab={Tabs.ADDRESS_BOOK}")


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
