from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

from checkout.models import CheckoutConfig

logger = logging.getLogger(__name__)


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
    user = order.user if order.user else None

    shipping = order.shipping_info
    items = []

    logger.info(f"Order: {order}")
    logger.info(f"Line Items: {order.lineitems.all()}")
    for item in order.lineitems.all():
        items.append({
            "title": item.product.title,
            "image_url": item.product.image,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": item.order_item_total
        })

    logger.info(f"ORDER ITEMS: {items}")

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
