from django import template

register = template.Library()


@register.filter(name='subtotal')
def subtotal(price, quantity):
    return price * quantity
