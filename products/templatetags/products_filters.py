from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


@register.filter(name='rating_format')
def rating_format(value):
    try:
        d = Decimal(value)
        if d % 1 == 0:
            return str(int(d))
        return f"{d:.1f}"
    except (InvalidOperation, ValueError, TypeError):
        return value
