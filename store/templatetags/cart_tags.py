from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        value = Decimal(str(value))
        arg = Decimal(str(arg))
        return value * arg
    except (ValueError, TypeError):
        return Decimal('0.00')

@register.filter
def aggregate_subtotal(items):
    try:
        return sum(item.price * item.quantity for item in items)
    except (ValueError, TypeError):
        return Decimal('0.00')