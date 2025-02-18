from django.conf import settings
from django.db import OperationalError, transaction, IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
)
import stripe
import logging
import time

from .models import Order, WebhookEvent
from .utils import send_order_confirmation_email, send_payment_failure_email


logger = logging.getLogger(__name__)

# Configure retry settings
WEBHOOK_RETRY_CONFIG = {
    "stop": stop_after_attempt(3),
    "retry": retry_if_exception_type((OperationalError,)),
}


# @retry(**WEBHOOK_RETRY_CONFIG)
def get_order_with_retry(payment_intent_id):
    for attempt in range(1, 6):
        try:
            order = Order.objects.get(stripe_pid=payment_intent_id,)
            return order
        except Order.DoesNotExist:
            if attempt < 5:  # Only sleep if not the final attempt
                time.sleep(1)
    return None

    # test_order = Order.objects.select_for_update().get(stripe_pid=payment_intent_id)
    # print(f"test_order: {test_order}")
    # return Order.objects.select_for_update().get(stripe_pid=payment_intent_id)


def handle_payment_event(payment_intent, event_type):
    try:
        with transaction.atomic():
            order = get_order_with_retry(payment_intent.id)

            if event_type == "payment_intent.succeeded":
                order.status = "complete"
                print("BLLAAAAA")
                logger.info(f"Processing payment for order {order.order_id}")
                send_order_confirmation_email(order)

            elif event_type == "payment_intent.payment_failed":
                logger.warning(f"Payment failed for order {order.order_id}")
                order.status = "failed"
                send_payment_failure_email(order)

            order.save()

            return True

    except Order.DoesNotExist:
        # logger.error(f"Order missing for PI {payment_intent.id}.")
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
        # logger.error(f"Duplicate event: {event.id}")
        return HttpResponse(status=400)

    if event.type in ["payment_intent.succeeded",
                      "payment_intent.payment_failed"]:
        payment_intent = event.data.object
        try:
            handle_payment_event(payment_intent, event.type)
        except Exception as e:
            # logger.error(f"Final attempt failed for {event.type}: {str(e)}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)
