from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("product_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Successfully logged in!")
            return redirect("product_list")
        else:
            messages.error(request,
                           "Invalid username or password. Please try again.")
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
