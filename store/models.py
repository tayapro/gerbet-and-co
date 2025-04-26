from django.db import models


class Faq(models.Model):
    """
    Represents a Frequently Asked Question (FAQ) entry.

    Each FAQ belongs to a specific section (e.g., Tasting & Treats,
    Orders, Payment) and contains a question and its corresponding answer.
    """

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
    """
    Stores a contact message submitted by a user through the Contact Us form.

    Captures the user's name, email address, message content,
    and the timestamp when the message was submitted.
    """

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.email} - {self.submitted_at}"


class Subscriber(models.Model):
    """
    Represents a newsletter subscriber.

    Stores the email address of the user who subscribed and the
    timestamp of subscription.
    """

    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
