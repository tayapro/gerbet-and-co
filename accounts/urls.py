from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

from .forms import CustomPasswordResetForm

"""
URL configuration for account-related views in the Gerbet & Co e-commerce
platform.

Includes routes for user registration, authentication (login/logout), profile
management,
address book operations (CRUD), order history viewing, and password management
(change and reset).
"""

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    path("account/profile/view", views.profile_view,
         name="profile_view"),
    path("account/profile/edit/", views.profile_edit,
         name="profile_edit"),
    path("account/address/list", views.address_list, name="address_list"),
    path("account/address/create/", views.address_create,
         name="address_create"),
    path("account/address/update/<int:id>/", views.address_update,
         name="address_update"),
    path("account/address/delete/<int:id>/", views.address_delete,
         name="address_delete"),
    path("address/set-default/<int:id>/", views.set_default_address,
         name="set_default_address"),
    path("account/order/list", views.order_list, name="order_list"),
    path("account/order/view/<int:id>/", views.order_view, name="order_view"),
    path("account/password/update", views.CustomPasswordChangeView.as_view(),
         name='password_update'),
    path("account/", views.account_view, name="account"),

    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/emails/password_reset_email.txt",
            html_email_template_name=(
                "accounts/emails/password_reset_email.html"),
            subject_template_name="accounts/emails/password_reset_subject.txt"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm"),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete"),
]
