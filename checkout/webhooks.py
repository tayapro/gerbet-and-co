from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import logging
import time

from .models import Order, WebhookEvent
from .utils import send_order_confirmation_email, send_payment_failure_email


logger = logging.getLogger(__name__)


def get_order_with_retry(payment_intent_id):
    for attempt in range(1, 6):
        try:
            order = Order.objects.get(stripe_pid=payment_intent_id,)
            return order
        except Order.DoesNotExist:
            if attempt < 5:
                time.sleep(1)

    logger.error(f"Order with Stripe PID {payment_intent_id} "
                 "not found after retries")

    messages.error(f"Order with Stripe PID {payment_intent_id} "
                   "not found after retries")

    raise Order.DoesNotExist(f"Order with Stripe PID {payment_intent_id} "
                             "not found after retries")


def handle_payment_event(payment_intent, event_type):
    try:
        order = get_order_with_retry(payment_intent.id)
        logger.info(f"webhooks handle_payment_event: order - {order}")

        if order.user_id:
            # Authenticated user order
            if not order.user or not order.user.email:
                logger.error(f"User {order.user}/{order.user.email} "
                             "has no email")
                messages.error("User account missing email")
                raise ValueError("User account missing email")
        else:
            # Guest order
            if not order.guest_email:
                logger.error(f"Guest order {order.id} missing email")
                messages.error("User account missing email")
                raise ValueError("Guest email required")

        logger.info(
            f"Handling {event_type} for order {order.id} - "
            f"User: {order.user_id}, Guest Email: {order.guest_email}, "
            f"Status: {order.status}, Amount: {order.grand_total}"
        )

        logger.debug(f"PaymentIntent metadata: {payment_intent.metadata}")

        if event_type == "payment_intent.succeeded":
            logger.debug(f"Email check - User exists: {bool(order.user)}, "
                         f"Guest email: {order.guest_email}")
            order.status = "paid"

            logger.info(f"WEBHOOK EMAIL: {order.email}")

            if not order.email:
                logger.error(
                    f"Missing email details - User: {order.user}, "
                    f"Guest Email: {order.guest_email}"
                )
                raise ValueError("Missing email for order confirmation")

            logger.info(f"Processing payment for order {order.id} to"
                        f" email {order.email}")

        elif event_type == "payment_intent.payment_failed":
            logger.warning(f"Payment failed for order {order.id}")
            order.status = "failed"

        order.save()

        # To reduce the risk of a race condition with the OrderItem table,
        # a short delay has been introduced here. Stripe may call the webhook
        # at the same time the user finalizes their order, so this ensures all
        # order items are saved before processing continues. Hence, the use
        # of sleep(5).
        if event_type == "payment_intent.succeeded":
            time.sleep(5)
            send_order_confirmation_email(order)
        elif event_type == "payment_intent.payment_failed":
            time.sleep(5)
            send_payment_failure_email(order)

        return True
    except Exception as e:
        logger.error(
            f"Payment handling failed - PI: {payment_intent.id}, "
            f"Amount: {payment_intent.amount}, "
            f"Currency: {payment_intent.currency}, "
            f"Error: {str(e)}",
            exc_info=True
        )
        return HttpResponse(status=400)


@csrf_exempt
def stripe_webhook(request):
    logger.warning("Webhook endpoint accessed - raw headers: %s",
                   dict(request.headers))
    logger.warning("Request body length: %d", len(request.body))

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Webhook exception: {e}")
        return HttpResponse(status=400)

    if WebhookEvent.objects.filter(stripe_id=event.id).exists():
        return HttpResponse(status=200)  # Event already processed

    try:
        webhook_event = WebhookEvent.objects.create(
            stripe_id=event.id,
            type=event.type,
            data={"payment_intent": event.data.object.id},
            processed=False,
        )
    except IntegrityError:
        logger.error(f"Duplicate event: {event.id}")
        return HttpResponse(status=400)

    if event.type in ["payment_intent.succeeded",
                      "payment_intent.payment_failed"]:
        payment_intent = event.data.object
        try:
            handle_payment_event(payment_intent, event.type)
            webhook_event.processed = True
            webhook_event.save(update_fields=["processed"])
        except Exception as e:
            logger.error(f"Final attempt failed for {event.type}: {str(e)}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)
