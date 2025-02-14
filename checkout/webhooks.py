# checkout/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import stripe

from .models import Order


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_payment_succeeded(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_payment_failed(payment_intent)
    # TODO: Add more event types

    return HttpResponse(status=200)


def handle_payment_succeeded(payment_intent):
    try:
        order = Order.objects.get(stripe_pid=payment_intent.id)
        order.status = 'complete'
        order.save()

        send_order_confirmation_email(order)

    except Order.DoesNotExist:
        pass


def handle_payment_failed(payment_intent):
    try:
        order = Order.objects.get(stripe_pid=payment_intent.id)
        order.status = 'failed'
        order.save()

        send_payment_failure_email(order)

    except Order.DoesNotExist:
        pass


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
