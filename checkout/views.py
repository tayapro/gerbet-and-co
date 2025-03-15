from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import logging
import stripe

from accounts.models import UserContactInfo
from products.models import Product
from .forms import ShippingInfoForm
from .models import CheckoutConfig, Order, OrderItem, ShippingInfo
from bag.bag import Bag


logger = logging.getLogger(__name__)


def checkout(request):
    bag = Bag(request)
    if bag.is_empty():
        return redirect("bag:view_bag")

    # Initialize essential variables
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    checkout_config = CheckoutConfig.objects.first()
    currency = (
        checkout_config.stripe_currency.lower()
        if checkout_config
        else "eur"
    )
    stripe.api_key = stripe_secret_key

    # Calculate totals
    bag_total = bag.get_total_price()
    delivery_cost = bag.get_delivery_cost()
    grand_total = bag.get_grand_total()
    grand_total_cents = int(grand_total * 100)

    # Handle existing order
    order_id = request.session.get("order_id")

    # Handle POST request
    if request.method == "POST":
        return handle_checkout_post(request, bag, order_id, currency)

    # Handle GET request (create new order)
    return handle_checkout_get(request, stripe_public_key, bag_total,
                               delivery_cost, grand_total, grand_total_cents,
                               currency)


def handle_checkout_get(request, stripe_public_key, bag_total, delivery_cost,
                        grand_total, grand_total_cents, currency):
    """Handle initial checkout page load"""
    # Create PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=grand_total_cents,
        currency=currency,
        automatic_payment_methods={"enabled": True},
    )

    shipping_info = ShippingInfo.objects.create(
        user=request.user if request.user.is_authenticated else None
    )
    # Create new Order
    order = Order.objects.create(
        order_total=bag_total,
        delivery_cost=delivery_cost,
        grand_total=grand_total,
        grand_total_cents=grand_total_cents,
        stripe_pid=intent.id,
        shipping_info=shipping_info
    )

    # Store order ID in session
    request.session["order_id"] = order.id
    request.session.modified = True

    # Prepare form
    initial = get_initial_shipping_data(request.user)
    form = ShippingInfoForm(
        user=request.user,
        initial=initial,
        # Hide fields already in User model for authenticated users
        instance=shipping_info if request.user.is_authenticated else None
    )

    # Build context
    context = build_checkout_context(
        request,
        form,
        stripe_public_key,
        intent,
        bag_total,
        delivery_cost,
        grand_total,
        grand_total_cents,
        currency,
        order.id
    )
    return render(request, "checkout/checkout.html", context)


def handle_checkout_post(request, bag, order_id, currency):
    """Handle form submission"""
    use_default = request.POST.get("use_default") == "on"
    logger.info(
        f"Checkout POST - User: {request.user}, "
        f"Authenticated: {request.user.is_authenticated}, "
        f"Use Default: {use_default}"
    )

    order = get_object_or_404(Order, id=order_id)
    logger.debug(
        f"Initial Order State - ID: {order.id}, "
        f"User: {order.user_id}, Guest Email: {order.guest_email}"
    )

    if request.user.is_authenticated and use_default:
        logger.info("Processing default address for authenticated user")
        default_address = UserContactInfo.objects.filter(
            user=request.user, is_default=True
        ).first()

        if default_address:
            logger.debug(
                f"Using default address - ID: {default_address.id}, "
                f"Email: {default_address.user.email}"
            )
            shipping_info = ShippingInfo.objects.create(
                user=request.user,
                phone_number=default_address.phone_number,
                street_address1=default_address.street_address1,
                street_address2=default_address.street_address2,
                town_or_city=default_address.town_or_city,
                county=default_address.county,
                postcode=default_address.postcode,
                country=default_address.country,
                is_default=True
            )

            order.user = request.user
            order.shipping_info = shipping_info
            order.save(update_fields=["user", "shipping_info"])

            return finalize_order(request, bag, order)

    form = ShippingInfoForm(request.POST, user=request.user)

    if not form.is_valid():
        return handle_invalid_form(request, form, currency)

    try:
        # Ensure it passes validation again
        if not form.is_valid():
            logger.error("Form validation failed again after correction: %s",
                         form.errors)
            messages.error(request, "There was an issue"
                           "with your address details.")
            return redirect("checkout")

        shipping_info = process_shipping_info(form, request.user)

        # Update order with shipping info
        update_order_details(order, request, shipping_info, form)

        # Process payment and finalize order
        return finalize_order(request, bag, order)

    except (Order.DoesNotExist, stripe.error.StripeError, Exception) as e:
        return handle_checkout_error(request, e)


# Helper functions
def get_full_name(request):
    """Get user's full name"""
    if request.user.is_authenticated:
        return f"{request.user.first_name} {request.user.last_name}"
    return ""


def get_initial_shipping_data(user):
    """Get initial data for shipping form"""
    initial = {}

    if user.is_authenticated:
        # From UserContactInfo if available
        default_address = UserContactInfo.objects.filter(
            user=user,
            is_default=True
        ).first()

        if default_address:
            initial.update({
                "street_address1": default_address.street_address1,
                "street_address2": default_address.street_address2,
                "town_or_city": default_address.town_or_city,
                "county": default_address.county,
                "postcode": default_address.postcode,
                "country": default_address.country,
                "phone_number": default_address.phone_number,
                "use_default": True
            })

            # For guest users
            initial.update({
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            })

    return initial


def process_shipping_info(form, user):
    """Process and save shipping information for both users and guests"""
    shipping_info = form.save(commit=False)

    # For authenticated users
    if user and user.is_authenticated:
        shipping_info.user = user
        if form.cleaned_data.get("save_as_default"):
            shipping_info.is_default = True

    # For guests (no user association)
    else:
        shipping_info.user = None
        shipping_info.is_default = False

    shipping_info.save()
    return shipping_info


def build_checkout_context(request, form, stripe_public_key, intent,
                           bag_total, delivery_cost, grand_total,
                           grand_total_cents, currency, order_id):
    """Build checkout context"""

    default_address = (
        UserContactInfo.objects.filter(user=request.user,
                                       is_default=True).first()
        if request.user.is_authenticated
        else None
    )

    return {
        "user": request.user,
        "form": form,
        "default_address": default_address,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
        "bag_total": bag_total,
        "delivery_cost": delivery_cost,
        "amount": grand_total_cents,
        "grand_total": grand_total,
        "currency": currency,
        "order_id": order_id,
        "stripe_pid": intent.id,
        "full_name": get_full_name(request),
    }


def create_order_items(bag, order):
    """Create order items from bag contents"""
    for item_id, item in bag.bag.items():
        product = get_object_or_404(Product, id=item_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item["quantity"],
            order_item_total=Decimal(item["price"]) * item["quantity"]
        )


def update_order_details(order, request, shipping_info, form):
    """Update order with user details"""
    order.shipping_info = shipping_info

    if request.user.is_authenticated:
        # Use authenticated user details
        order.user = request.user
    else:
        # Use guest details from validated form
        order.guest_email = form.cleaned_data["guest_email"]
        order.guest_first_name = form.cleaned_data["guest_first_name"]
        order.guest_last_name = form.cleaned_data["guest_last_name"]

    order.save(update_fields=[
        "shipping_info",
        "user",
        "guest_email",
        "guest_first_name",
        "guest_last_name"
    ])


def finalize_order(request, bag, order):
    """Finalize order processing"""
    try:
        logger.info(
            f"Finalizing order {order.id} - User: {order.user_id}, "
            f"Guest Email: {order.guest_email}, Status: {order.status}"
        )
        intent = stripe.PaymentIntent.retrieve(order.stripe_pid)
        logger.debug(f"PaymentIntent status: {intent.status}")
        logger.debug(f"Retrieved Stripe PaymentIntent: {intent}")

        if intent.status in {"requires_payment_method",
                             "requires_confirmation", "requires_action"}:
            logger.info("Confirming payment intent")
            intent = stripe.PaymentIntent.confirm(order.stripe_pid)
            logger.debug(f"Post-confirmation status: {intent.status}")

        if intent.status == "succeeded":
            logger.info("Payment succeeded, creating order items")
            create_order_items(bag, order)
            bag.clear()
            logger.debug(
                f"Updated Order State - ID: {order.id}, "
                f"User: {order.user_id}, Guest Email: {order.guest_email}, "
                f"Shipping Info: {order.shipping_info_id}"
            )
            logger.info(f"Order {order.id} finalized successfully")
            return redirect(reverse("checkout_success", args=[order.order_id]))

        logger.warning(
            f"Payment not successful - Status: {intent.status}, "
            f"Last Payment Error: {intent.last_payment_error}"
        )
        messages.error(request, f"Payment not successful: {intent.status}")
        return redirect("checkout")

    except stripe.error.CardError as e:
        err = e.json_body.get("error", {})
        logger.error(f"Stripe Card Error: {err}")
        messages.error(request, f"Card Error: {err.get('message')}")

    except Exception as e:
        logger.error(
            f"Order processing failed - Order: {order.id}, "
            f"User: {order.user_id}, Guest Email: {order.guest_email}, "
            f"Error: {str(e)}",
            exc_info=True
        )
        logger.error(f"Order processing failed: {e}")
        messages.error(request, f"Order processing failed: {e}")
        return redirect("checkout")


def handle_invalid_form(request, form, currency):
    """Handle invalid form submission"""
    # Log detailed form errors
    logger.error("Form validation failed with errors:")
    for field, errors in form.errors.items():
        logger.error(f"Field '{field}': {', '.join(errors)}")
        print(f"Field '{field}': {', '.join(errors)}")

    messages.error(request, "Please check your form entries")

    try:
        # Get existing order from session
        order_id = request.session.get("order_id")
        order = Order.objects.get(id=order_id)

        # Retrieve existing PaymentIntent
        intent = stripe.PaymentIntent.retrieve(order.stripe_pid)

        context = build_checkout_context(
            request=request,
            form=form,
            stripe_public_key=settings.STRIPE_PUBLIC_KEY,
            intent=intent,
            bag_total=order.order_total,
            delivery_cost=order.delivery_cost,
            grand_total=order.grand_total,
            grand_total_cents=order.grand_total_cents,
            currency=currency,
            order_id=order_id
        )

    except (Order.DoesNotExist, KeyError):
        # Fallback if order is missing
        context = {
            "form": form,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "currency": currency,
        }
        messages.warning(request, "Your session has expired, please try again")

    return render(request, "checkout/checkout.html", context)


def handle_checkout_error(request, error):
    """Handle checkout errors"""
    error_message = str(error)
    logger.error(f"Checkout error: {error_message}")
    messages.error(request, f"Order processing failed: {error_message}")
    return redirect("checkout")


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


@require_POST
@csrf_exempt
def cache_checkout_data(request):
    """
    Caches the checkout data in the session before confirming payment.
    """
    try:
        # Extract important fields from request.POST
        order_id = request.POST.get("order_id")
        if not Order.objects.filter(id=order_id).exists():
            messages.error(request, "Order not found")
            return JsonResponse({"error": "Order not found"}, status=400)

        payment_intent_id = request.POST.get("payment_intent_id")
        # Store data in session
        request.session["checkout_cache"] = request.POST.dict()
        if payment_intent_id:
            request.session["payment_intent_id"] = payment_intent_id
        request.session.modified = True
        return JsonResponse({"success": True})

    except Order.DoesNotExist:
        messages.error(request, "error: Order not found")
        return JsonResponse({"error": "Order not found"}, status=400)

    except Exception as e:
        messages.error(request, f"error: {e}")
        return JsonResponse({"error": str(e)}, status=500)
