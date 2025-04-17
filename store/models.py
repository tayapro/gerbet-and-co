from django.db import models


class Faq(models.Model):
    SECTION_CHOICES = [
        ("taste-and-treats", "Tasting & Treats"),
        ("your-sweet-account", "Your Sweet Profile"),
        ("orders", "Orders"),
        ("payment", "Payment"),
        ("delivery", "Delivery"),
    ]

    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.email} - {self.submitted_at}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
