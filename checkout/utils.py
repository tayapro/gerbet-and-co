from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from checkout.models import CheckoutConfig


def get_checkout_settings():
    settings, created = CheckoutConfig.objects.get_or_create(
        defaults={
            'free_delivery_threshold': 50.00,
            'delivery_cost': 5.00,
            'stripe_currency': 'eur',
        }
    )
    return settings


def get_email(order):
    # Get email from appropriate source
    return (
        order.user.email
        if order.user
        else getattr(order, 'guest_email', None)
    )


def send_order_confirmation_email(order):
    # recipient_email = get_email(order)
    recipient = [order.email]
    subject = f"Gerbet & Co Order Confirmation - #{order.order_id}"
    email_from = settings.EMAIL_HOST_USER

    # Prepare email content
    context = {"order": order}
    text_content = render_to_string(
        "checkout/emails/confirmation_email.txt", context)
    html_content = render_to_string(
        "checkout/emails/confirmation_email.html", context)

    # Create and send email
    email = EmailMultiAlternatives(subject, text_content, email_from,
                                   recipient)
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_payment_failure_email(order):
    print("send_payment_failure_email")
    # subject = f"Gerbet & Co - Payment Failed - Order #{order.order_id}"
    # body = render_to_string(
    #     'checkout/emails/payment_failed_email.txt',
    #     {'order': order}
    # )
    # send_mail(
    #     subject,
    #     body,
    #     settings.DEFAULT_FROM_EMAIL,
    #     [order.email]
    # )
