from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import time

from .models import Order, WebhookEvent
from .utils import send_order_confirmation_email, send_payment_failure_email


def get_order_with_retry(payment_intent_id):
    """
    Attempt to retrieve an order linked to a given Stripe PaymentIntent ID.

    Retries up to 5 times with 1-second intervals to handle potential database
    race conditions during order creation and webhook receipt.
    """

    for attempt in range(1, 6):
        try:
            order = Order.objects.get(stripe_pid=payment_intent_id,)
            return order
        except Order.DoesNotExist:
            if attempt < 5:
                time.sleep(1)

    messages.error(f"Order with Stripe PID {payment_intent_id} "
                   "not found after retries")

    raise Order.DoesNotExist(f"Order with Stripe PID {payment_intent_id} "
                             "not found after retries")


def handle_payment_event(payment_intent, event_type):
    """
    Process payment-related events for an order based on the incoming
    Stripe PaymentIntent object.

    Updates order status, sends confirmation or failure emails, and handles
    necessary database saves. Introduces a short delay to ensure all related
    records are saved before sending emails.
    """

    try:
        order = get_order_with_retry(payment_intent.id)

        if order.user_id:
            # Authenticated user order
            if not order.user or not order.user.email:
                raise ValueError("User account missing email")
        else:
            # Guest order
            if not order.guest_email:
                raise ValueError("Guest email required")

        if event_type == "payment_intent.succeeded":
            order.status = "paid"

            if not order.email:
                raise ValueError("Missing email for order confirmation")

        elif event_type == "payment_intent.payment_failed":
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
    except Exception:
        return HttpResponse(status=400)


@csrf_exempt
def stripe_webhook(request):
    """
    Main endpoint for receiving Stripe webhook events.

    Verifies event authenticity, prevents duplicate processing, and dispatches
    handling for payment success and payment failure events.
    """

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
        webhook_event = WebhookEvent.objects.create(
            stripe_id=event.id,
            type=event.type,
            data={"payment_intent": event.data.object.id},
            processed=False,
        )
    except IntegrityError:
        return HttpResponse(status=400)

    if event.type in ["payment_intent.succeeded",
                      "payment_intent.payment_failed"]:
        payment_intent = event.data.object
        try:
            handle_payment_event(payment_intent, event.type)
            webhook_event.processed = True
            webhook_event.save(update_fields=["processed"])
        except Exception:
            return HttpResponse(status=500)

    return HttpResponse(status=200)
