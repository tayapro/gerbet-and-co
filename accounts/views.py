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
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy

from checkout.models import Order
from .forms import (
    UserRegistrationForm,
    CustomPasswordChangeForm,
    UserProfileForm,
    AddressForm)
from .models import UserContactInfo
from .utils import send_welcome_email


def register(request):
    """
    Handle user registration by validating and creating a new user account.

    Sends a welcome email after successful registration. Redirects to login
    page with a success message on completion.
    """

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
            except ValidationError as e:
                form.add_error(None, e.messages)
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
    """
    Handle user login with authentication form validation.

    Supports 'Remember Me' functionality by adjusting session expiry.
    Redirects logged-in users directly to the product list page.
    """

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
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form, "next": next})


def logout(request):
    """
    Log the user out and redirect them to the home page with a success message.

    Handles unauthenticated access gracefully by redirecting to 'next'
    parameter.
    """

    next = request.GET.get("next", "/")

    if not request.user.is_authenticated:
        return redirect(next)

    if request.method == "POST":
        auth_logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("home")

    return render(request, "accounts/logout.html", {"next": next})


@login_required
def account_view(request):
    """
    Display the user's account overview page.
    """

    user = request.user

    return render(request, "accounts/account.html", {"user": user})


@login_required
def profile_view(request):
    """
    Display the user's personal profile details.
    """

    return render(request, "accounts/profile_view.html",
                  {"user": request.user})


@login_required
def profile_edit(request):
    """
    Allow users to edit and update their profile information.

    After a successful update, users are shown their updated profile.
    """

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             "Your profile has been successfully changed.")
            return render(request,
                          "accounts/profile_view.html", {"user": request.user})
    else:
        form = UserProfileForm(instance=request.user)

    return render(request,
                  "accounts/profile_edit.html",
                  {"form": form})


@login_required
def address_list(request):
    """
    Display all saved shipping addresses for the logged-in user.

    Highlights the default address and sorts addresses by default status and
    recency.
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
    """
    Allow users to create and save a new shipping address.

    Optionally set the newly created address as the default address.
    """

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


@login_required
def address_update(request, id):
    """
    Allow users to update an existing shipping address.

    Supports changing the default address selection during the update.
    """

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
    """
    Delete a specific shipping address from the user's saved addresses.

    Displays a success or error message based on the outcome.
    """

    address = get_object_or_404(UserContactInfo, id=id, user=request.user)

    try:
        address.delete()
        messages.success(request, "Address deleted successfully.")
    except Exception:
        messages.warning(request,
                         "Oops, something went wrong, "
                         "please try again.")
    return redirect(reverse('address_list'))


@login_required
@require_POST
@transaction.atomic
def set_default_address(request, id):
    """
    Set a specific address as the user's default shipping address.

    Resets the previous default address and saves the new selection atomically.
    """

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
    Display a list of past orders placed by the user.

    Orders are sorted by the most recent purchase first.
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
def order_view(request, id):
    """
    Display detailed information about a specific order.

    Ensures that users can only view their own orders.
    """

    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, "accounts/order_view.html", {"order": order})


class CustomPasswordChangeView(PasswordChangeView):
    """
    Handle user password changes with custom templates and redirect behavior.

    After successful password change, redirects user to the login page
    with a success notification.
    """

    template_name = "accounts/password_update.html"
    form_class = CustomPasswordChangeForm

    def form_valid(self, form):
        form.save()
        # Redirect to the login page with a success message
        return redirect(reverse_lazy("login") + "?password_change=success")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Handle password reset confirmations with a customized post-reset flow.

    After resetting the password, redirects the user to the login page
    with a success message.
    """

    def form_valid(self, form):
        form.save()

        # Redirect to the login page with a success message
        return redirect(reverse_lazy("login") + "?password_reset=success")
