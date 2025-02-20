from django.conf import settings
from django.db import OperationalError, transaction, IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import logging
import time

from .models import Order, WebhookEvent
from .utils import send_order_confirmation_email, send_payment_failure_email

import datetime


logger = logging.getLogger(__name__)


def get_order_with_retry(payment_intent_id):
    for attempt in range(1, 6):
        try:
            order = Order.objects.get(stripe_pid=payment_intent_id,)
            return order
        except Order.DoesNotExist:
            if attempt < 5:
                time.sleep(1)

    raise Exception("Run out of attempts")


def handle_payment_event(payment_intent, event_type):
    try:
        order = get_order_with_retry(payment_intent.id)

        now = datetime.datetime.now()
        print(f"order from handle_payment_event: {order}, time: {now.time()}")

        if event_type == "payment_intent.succeeded":
            order.status = "complete"
            now = datetime.datetime.now()
            print(f"order_email from handle_payment_event: {order.email}, "
                  f"time: {now.time()}")
            logger.info(f"Processing payment for order {order.order_id}")
            send_order_confirmation_email(order)

        elif event_type == "payment_intent.payment_failed":
            logger.warning(f"Payment failed for order {order.order_id}")
            order.status = "failed"
            send_payment_failure_email(order)

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
