from django.contrib import admin
from .models import DeliveryCosts


@admin.register(DeliveryCosts)
class DeliveryCostsAdmin(admin.ModelAdmin):
    list_display = ('free_delivery_threshold', 'delivery_cost')
