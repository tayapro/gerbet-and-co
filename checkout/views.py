from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import stripe

from .forms import ShippingInfoForm, OrderForm
from .models import CheckoutConfig, Order
from bag.bag import Bag


def create_payment_intent(order):
    checkout_config = CheckoutConfig.objects.first()
    currency = checkout_config.stripe_currency if checkout_config else "eur"

    intent = stripe.PaymentIntent.create(
        amount=int(order.total_price * 100),
        currency=currency.lower(),
        metadata={"order_id": str(order.order_id)}
    )

    return intent


def checkout(request):
    bag = Bag(request)
    if bag.is_empty():
        return redirect('bag:view_bag')

    sub_total = bag.get_total_price()
    delivery_cost = bag.get_delivery_cost()

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if not stripe_public_key:
        messages.warning(request,
                         "Stripe public key missing from configuration")

    if request.method == "POST":
        shipping_form = ShippingInfoForm(request.POST)
        order_form = OrderForm(request.POST)

        if shipping_form.is_valid() and order_form.is_valid():
            try:
                shipping_info = shipping_form.save()
                order = order_form.save(commit=False)
                order.total_price = sub_total + delivery_cost
                print(f"total price: {order.total_price}")

                if request.user.is_authenticated:
                    order.user = request.user

                order.shipping_info = shipping_info
                # order.save()

                # Create Stripe payment intent
                stripe.api_key = stripe_secret_key
                intent = create_payment_intent(order)
                print(f"stripe intent: {intent}")
                order.stripe_pid = intent.id
                order.stripe_payment_intent = intent.client_secret
                order.save()

                return redirect(reverse("checkout_success",
                                        args=[order.order_id]))

            except stripe.error.StripeError as e:
                print(f"stripe error: {e}")
                messages.error(request, messages.ERROR,
                               f"Payment error: {e.user_message}")
            except Exception as e:
                print(e)
                messages.error(request, messages.ERROR,
                               f"Error processing your order {e}")

    else:
        shipping_form = ShippingInfoForm()
        order_form = OrderForm()

    context = {
        "shipping_form": shipping_form,
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "bag_total": sub_total,
        "delivery_cost": delivery_cost,
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
