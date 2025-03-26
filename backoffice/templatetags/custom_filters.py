# backoffice/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def percentage(value, arg):
    """
    Calcule le pourcentage d'une valeur par rapport à une autre
    """
    try:
        return round((float(value) / float(arg)) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
        
@register.filter
def subtract(value, arg):
    """
    Soustrait arg de value
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0