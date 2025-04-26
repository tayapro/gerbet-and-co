from django.contrib import admin

from .models import ContactMessage, Faq, Subscriber


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for managing FAQ entries.

    Allows filtering by section, searching by question and answer content,
    and displays a short preview of the answer in the list view.
    """

    list_display = ("question", "section", "short_answer")
    list_filter = ("section",)
    search_fields = ("question", "answer")
    ordering = ("section",)

    def short_answer(self, obj):
        if len(obj.answer) > 75:
            return obj.answer[:75] + "..."
        return obj.answer

    short_answer.short_description = "Answer Preview"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for viewing Contact Us messages.

    Displays name, email, and submission date. Fields are read-only to
    prevent editing user-submitted content directly from the admin.
    """

    list_display = ("name", "email", "submitted_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "submitted_at")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for managing newsletter subscribers.

    Displays subscriber email addresses and their subscription timestamps.
    """

    list_display = ("email", "subscribed_at")
