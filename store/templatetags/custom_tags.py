from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    return value * arg

@register.filter
def total_amount(orders):
    """Calculate total amount of all orders"""
    return sum(order.quantity * order.utensil.price for order in orders)
