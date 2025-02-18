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


def send_order_confirmation_email(order):
    print(f"order.email: {order.email}")
    recipient = [order.email]
    subject = f"Order Confirmation - #{order.order_id}"
    email_from = settings.EMAIL_HOST_USER
    print(f"recipient: {recipient}, subject: {subject}, email_from: {email_from}")

    # Prepare email content
    context = {"order": order}
    print(f"context: {context}")
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
    # subject = f"Payment Failed - Order #{order.order_id}"
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

