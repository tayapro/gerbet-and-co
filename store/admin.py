from django.contrib import admin

from .models import ContactMessage, Faq


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
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
    list_display = ("name", "email", "submitted_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "submitted_at")
