import uuid
from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

from products.models import Product


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                             blank=True)
    is_default = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20)
    street_address1 = models.CharField(max_length=256)
    street_address2 = models.CharField(max_length=256, blank=True, null=True)
    town_or_city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(blank_label="Country", null=False, blank=False)
    postcode = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_default and self.user:
            ShippingInfo.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

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
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    shipping_info = models.ForeignKey(ShippingInfo, on_delete=models.CASCADE)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total_cents = models.PositiveIntegerField(default=0)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
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
        if self.user:
            name = f"{self.user.first_name} {self.user.last_name}"
        else:
            name = "Guest User"
        return f"Order {self.order_id} - {name}, email {self.email}"

    class Meta:
        indexes = [
            models.Index(fields=['stripe_pid'])
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    order_item_total = models.DecimalField(max_digits=6, decimal_places=2,
                                           null=False, blank=False,
                                           editable=False)

    def save(self, *args, **kwargs):
        self.order_item_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'The {self.product.title} on order {self.order.order_id}'


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
