from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import logging
import stripe

from .forms import ShippingInfoForm, OrderForm
from .models import CheckoutConfig, Order, ShippingInfo
from bag.bag import Bag

logger = logging.getLogger(__name__)


def checkout(request):
    bag = Bag(request)
    if bag.is_empty():
        return redirect('bag:view_bag')

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    grand_total = int(bag.get_grand_total() * 100)
    checkout_config = CheckoutConfig.objects.first()
    currency = (
        checkout_config.stripe_currency.lower()
        if checkout_config else 'eur')

    print(f"REQUEST.SESSION: {request.session}")

    # Handle POST request
    if request.method == "POST":
        shipping_form = ShippingInfoForm(request.POST)
        order_form = OrderForm(request.POST)

        if shipping_form.is_valid() and order_form.is_valid():
            try:
                order_id = request.session.get('order_id')
                payment_intent_id = request.session.get('payment_intent_id')

                if not order_id or not payment_intent_id:
                    messages.error(request,
                                   "Session expired, please try again")
                    return redirect('checkout')

                order = Order.objects.get(id=order_id)

                shipping_info = shipping_form.save()
                order_form_instance = order_form.save(commit=False)

                order.shipping_info = shipping_info
                order.email = order_form_instance.email

                if request.user.is_authenticated:
                    order.user = request.user

                # Retrieve the PaymentIntent
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                print(f"Retrieved PaymentIntent: {intent}")

                # Confirm the PaymentIntent if necessary
                if intent.status in {
                        "requires_payment_method",
                        "requires_confirmation",
                        "requires_action", }:
                    intent = stripe.PaymentIntent.confirm(payment_intent_id)
                    print(f"Confirmed PaymentIntent: {intent}")

                if intent.status == 'succeeded':
                    # Clean up, order status will handled by webhook
                    bag.clear()
                    del request.session['payment_intent_id']
                    del request.session['order_id']

                    return redirect(reverse("checkout_success",
                                            args=[order.order_id]))
                else:
                    messages.error(request,
                                   f"Payment not successful: {intent.status}")
                    return redirect('checkout')
            except Order.DoesNotExist:
                messages.error(request, "Order not found")
                return redirect('checkout')

            except stripe.error.StripeError as e:
                messages.error(request, f"Payment error: {e.user_message}")
                return redirect('checkout')
            except Exception as e:
                messages.error(request, f"Order processing failed: {e}")
                print(f"Order processing failed: {e}")
                return redirect('checkout')
        else:
            messages.error(request, "Please check your form entries")
            context = {
                "shipping_form": shipping_form,
                "order_form": order_form,
                "stripe_public_key": stripe_public_key,
                "client_secret": request.session.get('client_secret'),
                "bag_total": bag.get_total_price(),
                "delivery_cost": bag.get_delivery_cost(),
                "amount": grand_total,
                "grand_total": bag.get_grand_total(),
                "currency": currency,
            }
            return render(request, "checkout/checkout.html", context)

    # Handle GET request
    intent = stripe.PaymentIntent.create(
        amount=grand_total,
        currency=currency,
        automatic_payment_methods={"enabled": True},)

    order = Order.objects.create(
            grand_total=grand_total,
            stripe_payment_intent=intent.client_secret,
            stripe_pid=intent.id,
            shipping_info=ShippingInfo.objects.create())

    # Save order_id and stripe_pid in the session
    request.session['order_id'] = order.id
    request.session['payment_intent_id'] = intent.id

    print(f"ORDER: {order}")

    context = {
        "shipping_form": ShippingInfoForm(),
        "order_form": OrderForm(),
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
        "bag_total": bag.get_total_price(),
        "delivery_cost": bag.get_delivery_cost(),
        "amount": grand_total,
        "grand_total": bag.get_grand_total(),
        "currency": currency,
        "order_id": request.session['order_id'],
        "stripe_pid": request.session['stripe_pid'],
    }
    return render(request, "checkout/checkout.html", context)


def checkout_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if "bag" in request.session:
        del request.session["bag"]
        request.session.modified = True

    messages.success(request,
                     (f"Thank you! Your order {order.order_id} "
                      "was placed successfully."))

    context = {
        "order": order,
    }
    return render(request, "checkout/checkout_success.html", context)
