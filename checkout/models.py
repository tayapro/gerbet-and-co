from django.db import models


class DeliveryCosts(models.Model):
    free_delivery_threshold = models.DecimalField(max_digits=10,
                                                  decimal_places=2,
                                                  default=50.00)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2,
                                        default=5.00)

    class Meta:
        verbose_name = "Delivery Costs"
        verbose_name_plural = "Delivery Costs"

    def __str__(self):
        return (
            "Delivery Settings (Free Over "
            f"{self.free_delivery_threshold:.2f} euro, "
            f"Cost: {self.delivery_cost:.2f} euro)")
