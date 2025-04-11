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
import logging

from checkout.models import Order
from .forms import (
    UserRegistrationForm,
    CustomPasswordChangeForm,
    UserProfileForm,
    AddressForm)
from .models import UserContactInfo
from .utils import send_welcome_email

logger = logging.getLogger(__name__)


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
    user = request.user

    return render(request, "accounts/account.html", {"user": user})


@login_required
def profile_view(request):
    return render(request, "accounts/profile_view.html",
                  {"user": request.user})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            context = {
                "user": request.user,
                "toast_message": "Your profile has been successfully changed.",
            }
            return render(request,
                          "accounts/profile_view.html",
                          context)
    else:
        form = UserProfileForm(instance=request.user)

    return render(request,
                  "accounts/profile_edit.html",
                  {"form": form})


@login_required
def address_list(request):
    """
    Display a list of saved addresses for the user.
    """
    user = request.user
    addresses = (
        UserContactInfo.objects
        .filter(user=user)
        .order_by('-is_default', '-updated_at')
    )

    context = {
        "user": user,
        "addresses": addresses
    }

    return render(request, "accounts/address_list.html", context)


@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            try:
                address = form.save(commit=False)
                address.user = request.user
                if form.cleaned_data["set_as_default"]:
                    UserContactInfo.objects.filter(
                        user=request.user, is_default=True
                    ).update(is_default=False)
                    address.is_default = True
                address.save()
                messages.success(request, "New address added successfully.")
                return redirect("address_list")
            except Exception:
                return render(request, "accounts/address_form.html",
                              {"form": form})
        else:
            return render(request, "accounts/address_form.html",
                          {"form": form})
    else:
        form = AddressForm()

    return render(request, "accounts/address_form.html", {"form": form})


# @login_required
# def address_view(request):
#     addresses = UserContactInfo.objects.filter(user=request.user)

#     return render(request, "accounts/address_view.html",
#                   {"addresses": addresses})


@login_required
def address_update(request, id):
    address = get_object_or_404(UserContactInfo, id=id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            if form.cleaned_data["set_as_default"]:
                UserContactInfo.objects.filter(
                    user=request.user, is_default=True
                ).exclude(id=address.id).update(is_default=False)
                address.is_default = True
            else:
                address.is_default = False
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect("address_list")
    else:
        form = AddressForm(instance=address, initial={
            "set_as_default": address.is_default
        })

    context = {
        "form": form,
        "address": address,
    }
    return render(request, "accounts/address_form.html", context)


@login_required
@require_POST
def address_delete(request, id):
    address = get_object_or_404(UserContactInfo, id=id, user=request.user)

    try:
        address.delete()
        messages.success(request, "Address deleted successfully.")
    except Exception as e:
        messages.warning(request,
                         "Oops, something went wrong, "
                         "please try again.")
        logger.error(f"Error deleting address: {e}")
    return redirect(reverse('address_list'))


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
    return redirect(reverse('address_list'))


@login_required
def order_list(request):
    """
    Display a list of orders for the user.
    """
    user = request.user
    orders = (
        Order.objects
        .filter(user=user)
        .order_by('-created_at')
    )

    context = {
        "user": user,
        "orders": orders
    }

    return render(request, "accounts/order_list.html", context)

@login_required
def order_view(request):
    return render(request, "home.html")


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
