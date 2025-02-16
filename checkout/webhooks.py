from django.conf import settings
from django.core.mail import send_mail
from django.db import OperationalError, transaction, IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
import stripe
import logging

from .models import Order, WebhookEvent


logger = logging.getLogger(__name__)

# Configure retry settings
WEBHOOK_RETRY_CONFIG = {
    "stop": stop_after_attempt(3),
    "wait": wait_exponential(multiplier=1, min=2, max=10),
    "retry": retry_if_exception_type((OperationalError,)),
}


@retry(**WEBHOOK_RETRY_CONFIG)
def get_order_with_retry(payment_intent_id):
    return Order.objects.select_for_update().get(stripe_pid=payment_intent_id)


def handle_payment_event(payment_intent, event_type):
    try:
        with transaction.atomic():
            order = get_order_with_retry(payment_intent.id)

            if event_type == "payment_intent.succeeded":
                logger.info(f"Processing payment for order {order.order_id}")
                order.status = "complete"
                send_order_confirmation_email(order)

            elif event_type == "payment_intent.payment_failed":
                logger.warning(f"Payment failed for order {order.order_id}")
                order.status = "failed"

            order.save()
            return True

    except Order.DoesNotExist:
        logger.error(f"Order missing for PI {payment_intent.id}.")
        raise


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if WebhookEvent.objects.filter(stripe_id=event.id).exists():
        return HttpResponse(status=200)  # Event already processed

    try:
        WebhookEvent.objects.create(
            stripe_id=event.id,
            type=event.type,
            data=dict(event)
        )
    except IntegrityError:
        logger.error(f"Duplicate event: {event.id}")
        return HttpResponse(status=400)

    if event.type in ["payment_intent.succeeded",
                      "payment_intent.payment_failed"]:
        payment_intent = event.data.object
        try:
            handle_payment_event(payment_intent, event.type)
        except Exception as e:
            logger.error(f"Final attempt failed for {event.type}: {str(e)}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)


def send_order_confirmation_email(order):
    print("send_order_confirmation_email")
    # subject = f"Order Confirmation - #{order.order_id}"
    # body = render_to_string(
    #     'checkout/emails/confirmation_email.txt',
    #     {'order': order}
    # )
    # send_mail(
    #     subject,
    #     body,
    #     settings.DEFAULT_FROM_EMAIL,
    #     [order.email]
    # )


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
