from decimal import Decimal
from django import template

register = template.Library()


@register.filter(name='subtotal')
def subtotal(price, quantity):
    return Decimal(str(price)) * Decimal(quantity)
