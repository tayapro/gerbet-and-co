from django.db import models


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
