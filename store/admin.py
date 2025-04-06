from django.contrib import admin
from .models import Faq


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
