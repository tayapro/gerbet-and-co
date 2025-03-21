from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timezone, timedelta
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
        messages.error(request, "Your shopping bag is empty. "
                       "Please add items before checking out.")
        return redirect("product_list")

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

    # Store PaymentIntent creation time in session
    request.session["payment_intent_created_at"] = (
        datetime.now(timezone.utc).isoformat()
    )
    request.session.modified = True

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

    order = get_order_or_redirect(order_id, request)
    if not isinstance(order, Order):
        return order

    check_payment_session(request, order)

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
        logger.error("handle_checkout_post: form is invalid")
        return handle_invalid_form(request, form, currency)

    context = {"form": form, "order": order}

    if form.is_valid():
        try:
            shipping_info = process_shipping_info(form, request.user)

            # Update order with shipping info
            update_order_details(order, request, shipping_info, form)

            # Finalize order
            return finalize_order(request, bag, order)

        except (Order.DoesNotExist, stripe.error.StripeError, Exception) as e:
            form.add_error(None, e)
            return render(request, "checkout/checkout.html", context)
    else:
        form.add_error(None, "please make changes.")
        return render(request, "checkout/checkout.html", context)


@require_POST
@csrf_exempt
def cache_checkout_data(request):
    """
    Caches the checkout data in the session before confirming payment.
    """
    logger.info("cache_checkout_data")
    for key, value in request.session.items():
        logger.info(f"Key: {key}, Value: {value}")
        print(f"Key: {key}, Value: {value}")

    try:
        order_id = request.POST.get("order_id")
        if not order_id:
            return JsonResponse({"error": "Missing order ID."}, status=400)

        order = get_order_or_redirect(order_id, request)
        if not isinstance(order, Order):
            return order

        session_check = check_payment_session(request, order)
        if isinstance(session_check, JsonResponse):
            return session_check

        user_email = request.POST.get("user_email") or (
            request.user.email if request.user.is_authenticated else None
        )

        user_fullname = get_full_name(request)

        # Cache data in session
        request.session["checkout_cache"] = {
            "order_id": order_id,
            "user_email": user_email,
        }

        payment_intent_id = request.POST.get("payment_intent_id")
        if payment_intent_id:
            request.session["payment_intent_id"] = payment_intent_id

            # Try to update Stripe metadata
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.PaymentIntent.modify(payment_intent_id, metadata={
                    "order_id": order.id,
                    "user_email": user_email,
                    "user_fullname": user_fullname,
                })
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error: {str(e)}")
                return JsonResponse({
                    "error": "Failed to update payment metadata with Stripe.",
                    "details": str(e),
                }, status=500)

        request.session.modified = True

        return JsonResponse({"success": True}, status=200)

    except KeyError as e:
        logger.error(f"Missing field in request: {str(e)}")
        return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
    except Exception as e:
        logger.error(f"Cache checkout data error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Failed to cache checkout data",
                             "details": str(e)}, status=500)


# Helper functions
def handle_expired_payment_session(request, order):
    """
    Handles expired payment sessions by canceling the PaymentIntent
    and clearing session data.
    """
    try:
        stripe.PaymentIntent.cancel(order.stripe_pid)
        # messages.error(request, "Your session has expired. "
        #                "Please restart checkout.")
        request.session["payment_intent_created_at"] = None
        request.session["order_id"] = None
        request.session["checkout_cache"] = None
        request.session.modified = True
    except Exception as e:
        messages.error(request, "An error occurred while canceling your "
                       "payment. Please try again.")
        logger.error("Payment cancelling error: Stripe_pid "
                     f"{order.stripe_pid} - {str(e)}")


def check_payment_session(request, order):
    """
    Validates the payment session and handles expiration.
    """
    payment_created_at = request.session.get("payment_intent_created_at")
    if payment_created_at:
        try:
            # Convert the ISO 8601 string into a datetime object
            payment_created_at = datetime.fromisoformat(payment_created_at)
            # Make it timezone-aware
            request.session["payment_intent_created_at"] = (
                datetime.now(timezone.utc).isoformat()
            )
        except ValueError:
            messages.error(request, "Invalid session data. "
                           "Please restart checkout.")
            request.session["payment_intent_created_at"] = None
            return JsonResponse({"error": "Invalid session data. "
                                 "Please restart checkout."}, status=400)

        # Check if the session has expired
        if (
            datetime.now(timezone.utc) - payment_created_at
            > timedelta(hours=1)
        ):
            handle_expired_payment_session(request, order)
            return JsonResponse({"error": "Your session has expired. "
                                 "Please restart checkout."}, status=400)

        return None


def get_order_or_redirect(order_id, request):
    """
    Unified order retrieval that handles:
    - AJAX requests (returns JSON)
    - Regular requests (returns redirect)
    - Session expiration checks
    """
    try:
        order = Order.objects.get(id=order_id)
        logger.debug(
            f"Initial Order State - ID: {order.id}, "
            f"User: {order.user_id}, Guest Email: {order.guest_email}"
        )
        return order
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} not found.")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                "error": "order_not_found",
                "redirect_url": reverse("checkout")
            }, status=404)

        return JsonResponse({
                "error": "order_not_found",
                "redirect_url": reverse("checkout")
            }, status=404)


def get_full_name(request):
    """Get user's full name"""
    if request.user.is_authenticated:
        return f"{request.user.first_name} {request.user.last_name}"
    return "Guest"


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
            return render(request, "checkout/checkout_success.html",
                          {"order": order})

        logger.warning(
            f"Payment not successful - Status: {intent.status}, "
            f"Last Payment Error: {intent.last_payment_error}"
        )
        messages.error(request, f"Payment not successful: {intent.status}")

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

    return render(request, "checkout/checkout.html",
                  {"order": order})


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

    except Order.DoesNotExist:
        messages.warning("handle_invalid_form: order does not exist")
        return redirect("checkout")

    except KeyError as e:
        messages.warning(request, f"Invalid form error: {e}")
        context = {
            "form": form,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "currency": currency,
        }

    return render(request, "checkout/checkout.html", context)


def checkout_success(request, order_id):
    order = get_order_or_redirect(order_id, request)
    if not isinstance(order, Order):
        return order

    # List of session keys to delete
    session_keys_to_delete = ["bag",
                              "order_id",
                              "checkout_cache",
                              "payment_intent_created_at"]

    for key in session_keys_to_delete:
        if key in request.session:
            del request.session[key]

    request.session.modified = True

    context = {
        "order": order,
    }
    return render(request, "checkout/checkout_success.html", context)
