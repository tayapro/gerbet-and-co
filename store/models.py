from django.db import models


class Faq(models.Model):
    SECTION_CHOICES = [
        ("taste-and-treats", "Tasting & Treats"),
        ("your-sweet-account", "Your Sweet Profile"),
        ("orders", "Orders"),
        ("payment", "Payment"),
        ("delivery", "Delivery"),
        ("contact", "Still Curious? Contact Us"),
    ]

    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question
