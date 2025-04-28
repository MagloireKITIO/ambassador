from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """
    Soustraction de deux nombres dans les templates
    Exemple d'utilisation: {{ first_number|sub:second_number }}
    """
    try:
        # Convertir en Decimal pour éviter les problèmes de précision
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError):
        try:
            # Essayer avec des float si Decimal échoue
            return float(value) - float(arg)
        except (ValueError, TypeError):
            return 0