from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import logging
import stripe
import uuid


from .forms import ShippingInfoForm, OrderForm
from .models import CheckoutConfig, Order, ShippingInfo
from bag.bag import Bag

logger = logging.getLogger(__name__)


def create_payment_intent(order):
    checkout_config = CheckoutConfig.objects.first()
    currency = checkout_config.stripe_currency if checkout_config else "eur"
    intent = stripe.PaymentIntent.create(
        amount=int(order.grand_total * 100),
        currency=currency.lower(),
        automatic_payment_methods={
            'enabled': True,
        },
        metadata={"order_id": str(order.order_id)}
    )
    return intent


def checkout(request):
    bag = Bag(request)
    if bag.is_empty():
        return redirect('bag:view_bag')

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    grand_total = bag.get_grand_total()
    checkout_config = CheckoutConfig.objects.first()
    currency = checkout_config.stripe_currency.lower() if checkout_config else 'eur'

    # Create temporary order early for ID reference
    if 'order_id' not in request.session:
        stripe_pid = str(uuid.uuid4())
        temp_order = Order.objects.create(
            status='pending',
            stripe_pid=stripe_pid,
            grand_total=grand_total,
            email='temp@example.com',  # Will be updated later
            shipping_info=ShippingInfo.objects.create()
        )
        request.session['order_id'] = str(temp_order.order_id)
        request.session['stripe_pid'] = stripe_pid
        logger.info(f"Created temporary order with ID: {temp_order.order_id} and stripe_pid: {temp_order.stripe_pid}")
    elif "stripe_pid" not in request.session:
        order = Order.objects.get(order_id=request.session['order_id'])
        request.session['stripe_pid'] = order.stripe_pid

    if request.method == "GET":
        try:
            # Create PaymentIntent with order ID in metadata
            intent = stripe.PaymentIntent.create(
                amount=int(grand_total * 100),
                currency=currency,
                automatic_payment_methods={'enabled': True},
                metadata={
                    "order_id": request.session['order_id'],
                    "stripe_pid": request.session['stripe_pid'],
                    "status": "initialized"
                }
            )
            request.session['payment_intent_id'] = intent.id
            client_secret = intent.client_secret
            logger.info(f"Created PaymentIntent with ID: {intent.id} for order ID: {request.session['order_id']}")
        except Exception as e:
            messages.error(request, "Payment system error")
            logger.error(f"Payment system error: {e}")
            return redirect('bag:view_bag')

    elif request.method == "POST":
        payment_intent_id = request.session.get('payment_intent_id')
        order_id = request.session.get('order_id')

        if not payment_intent_id or not order_id:
            messages.error(request, "Session expired, please try again")
            return redirect('checkout')

        shipping_form = ShippingInfoForm(request.POST)
        order_form = OrderForm(request.POST)

        if shipping_form.is_valid() and order_form.is_valid():
            try:
                # Get existing temporary order
                order = Order.objects.get(order_id=order_id)
                logger.info(f"Retrieved order with ID: {order.order_id}")

                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                # Only update if payment hasn't succeeded yet
                if intent.status in ['requires_payment_method',
                                     'requires_confirmation',
                                     'requires_action']:
                    if intent.amount != int(grand_total * 100):
                        intent = stripe.PaymentIntent.modify(
                            payment_intent_id,
                            amount=int(grand_total * 100),
                            metadata={
                                "order_id": str(order.order_id),
                                "status": "finalized"
                            }
                        )
                        logger.info(f"Modified PaymentIntent with ID: {intent.id} for order ID: {order.order_id}")
                elif intent.status == 'succeeded':
                    logger.info("Using pre-completed payment intent")
                    order.status = 'processing'
                else:
                    messages.error(request, f"Cannot handle payment status: {intent.status}")
                    return redirect('checkout')

                shipping_info = shipping_form.save()
                order_form_instance = order_form.save(commit=False)

                order.grand_total = grand_total
                order.stripe_pid = intent.id
                order.stripe_payment_intent = intent.client_secret
                order.shipping_info = shipping_info
                order.status = 'processing'

                if request.user.is_authenticated:
                    order.user = request.user

                order.email = order_form_instance.email

                order.save()
                bag.clear()

                # Clean up session
                del request.session['payment_intent_id']
                del request.session['order_id']

                return redirect(reverse("checkout_success", args=[order.order_id]))

            except stripe.error.StripeError as e:
                messages.error(request, f"Payment error: {e.user_message}")
                logger.error(f"Payment error: {e.user_message}")
            except Exception as e:
                messages.error(request, f"Order processing failed: {e}")
                logger.error(f"Order processing failed: {e}")
            return redirect('checkout')

        else:  # Form validation failed
            messages.error(request, "Please check your form entries")
            context = {
                "shipping_form": shipping_form,
                "order_form": order_form,
                "stripe_public_key": stripe_public_key,
                "client_secret": intent.client_secret,
                "bag_total": bag.get_total_price(),
                "delivery_cost": bag.get_delivery_cost(),
                "amount": int(grand_total * 100),
                "grand_total": grand_total,
                "currency": currency,
                "order_id": request.session['order_id'],
                "stripe_pid": request.session['stripe_pid'],
            }
            return render(request, "checkout/checkout.html", context)

    # GET request handling
    context = {
        "shipping_form": ShippingInfoForm(),
        "order_form": OrderForm(),
        "stripe_public_key": stripe_public_key,
        "client_secret": client_secret,
        "bag_total": bag.get_total_price(),
        "delivery_cost": bag.get_delivery_cost(),
        "amount": int(grand_total * 100),
        "grand_total": grand_total,
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
