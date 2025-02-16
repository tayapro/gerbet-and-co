import uuid
from django.db import models
from django.contrib.auth.models import User


class CheckoutConfig(models.Model):
    free_delivery_threshold = models.DecimalField(max_digits=10,
                                                  decimal_places=2,
                                                  default=50.00)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2,
                                        default=5.00)
    stripe_currency = models.CharField(max_length=3, default="eur")

    class Meta:
        verbose_name = "Checkout Configuration"
        verbose_name_plural = "Checkout Configurations"

    def __str__(self):
        return (
            "Checkout Settings (Free Over "
            f"{self.free_delivery_threshold:.2f} euro, "
            f"Cost: {self.delivery_cost:.2f} euro, "
            f"Currency: {self.stripe_currency})")


class ShippingInfo(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    street_address1 = models.CharField(max_length=256)
    street_address2 = models.CharField(max_length=256, blank=True, null=True)
    town_or_city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Shipping Info for {self.full_name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4,
                                editable=False, unique=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True)
    email = models.EmailField()
    shipping_info = models.ForeignKey(ShippingInfo, on_delete=models.CASCADE)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total_cents = models.PositiveIntegerField(default=0)
    stripe_payment_intent = models.CharField(max_length=255,
                                             null=True, blank=True,
                                             unique=True)
    stripe_pid = models.CharField(max_length=255, null=False,
                                  blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.grand_total_cents = int(self.grand_total * 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Order {self.order_id} - {self.shipping_info.full_name}, "
                f"status {self.status}, grand total {self.grand_total}, "
                f"stripe_payment_intent {self.stripe_payment_intent}, "
                f"stripe_pid {self.stripe_pid}")

    class Meta:
        indexes = [
            models.Index(fields=['stripe_pid'])
        ]


# class OrderItem(models.Model):
#     quantity = models.IntegerField(null=False, blank=False, default=0)
#     order_item_total = 


class WebhookEvent(models.Model):
    stripe_id = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)

    def __str__(self):
        return f"{self.type} ({self.stripe_id})"
