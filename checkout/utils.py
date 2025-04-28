from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from checkout.models import CheckoutConfig


def get_checkout_settings():
    """
    Retrieve or create checkout settings from the CheckoutConfig model.

    Returns the checkout settings used for delivery cost,
    free delivery thresholds, and Stripe currency configuration.
    """

    settings, created = CheckoutConfig.objects.get_or_create(
        defaults={
            'free_delivery_threshold': 50.00,
            'delivery_cost': 5.00,
            'stripe_currency': 'eur',
        }
    )
    return settings


def send_order_confirmation_email(order):
    """
    Send a confirmation email to the user after a successful order.

    Renders both text and HTML versions of the email and sends using
    Django's EmailMultiAlternatives.
    """

    context = prepare_confirmation_email_details(order)
    recipient = [context["email"]]
    subject = f"Gerbet & Co Order Confirmation - #{order.order_id}"
    email_from = settings.EMAIL_HOST_USER

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
    """
    Send a payment failure email notification to the user if
    the Stripe payment process fails.

    Provides a link to customer support in the message.
    """

    context = prepare_payment_failure_email_details(order)
    recipient = [context["email"]]
    subject = f"Gerbet & Co Payment Failed - Order #{order.order_id}"
    email_from = settings.EMAIL_HOST_USER

    text_content = render_to_string(
        "checkout/emails/payment_failed_email.txt", context)
    html_content = render_to_string(
        "checkout/emails/payment_failed_email.html", context)

    email = EmailMultiAlternatives(subject, text_content, email_from,
                                   recipient)
    email.attach_alternative(html_content, "text/html")
    email.send()


def prepare_confirmation_email_details(order):
    """
    Prepare the context dictionary for rendering order confirmation emails.

    Gathers order details, user or guest information, shipping address,
    and ordered products.
    """

    user = order.user if order.user else None

    shipping = order.shipping_info
    items = []

    for item in order.lineitems.all():
        items.append({
            "title": item.product.title,
            "image_url": item.product.image,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": item.order_item_total
        })

    return {
        "order_id": order.order_id,
        "email": user.email if user else order.guest_email,
        "first_name": user.first_name if user else order.guest_first_name,
        "last_name": user.last_name if user else order.guest_last_name,
        "address_line1": shipping.street_address1,
        "address_line2": shipping.street_address2,
        "town_or_city": shipping.town_or_city,
        "postcode": shipping.postcode,
        "country": shipping.country,
        "phone_number": shipping.phone_number,
        "delivery_cost": order.delivery_cost,
        "subtotal": order.grand_total,
        "grand_total": order.order_total,
        "items": items
    }


def prepare_payment_failure_email_details(order):
    """
    Prepare the context dictionary for rendering payment failure emails.

    Gathers order ID, recipient information, and a support URL link.
    """

    user = order.user if order.user else None

    return {
        "order_id": order.order_id,
        "email": user.email if user else order.guest_email,
        "first_name": user.first_name if user else order.guest_first_name,
        "last_name": user.last_name if user else order.guest_last_name,
        "support_url": (
            "https://gerbet-and-co-84c4ca4e68bb.herokuapp.com/contact-us/"
        )
    }
