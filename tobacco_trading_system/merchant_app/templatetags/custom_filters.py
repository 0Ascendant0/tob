from django import template
from django.db.models import Avg

register = template.Library()


@register.filter(name='average')
def average(value, arg=None):
    """Template filter to compute average.

    Usage:
      - For a queryset and field name: {{ queryset|average:"field_name" }}
      - For a list of numbers: {{ numbers|average }}
      - For a list of objects and attribute name: {{ objects|average:"attr_name" }}

    Returns 0 when no values found or on error.
    """
    try:
        # If it's a Django queryset (has aggregate), and arg provided, use DB aggregation
        if hasattr(value, 'aggregate') and arg:
            res = value.aggregate(avg=Avg(arg))
            return res.get('avg') or 0

        # Otherwise, try to iterate and compute average in Python
        iterable = list(value or [])
        if not iterable:
            return 0

        numbers = []
        if arg:
            for item in iterable:
                # support attribute or dict lookup
                val = None
                try:
                    val = getattr(item, arg)
                except Exception:
                    try:
                        val = item.get(arg)
                    except Exception:
                        val = None
                if val is not None:
                    try:
                        numbers.append(float(val))
                    except Exception:
                        continue
        else:
            for item in iterable:
                try:
                    numbers.append(float(item))
                except Exception:
                    continue

        if not numbers:
            return 0
        return sum(numbers) / len(numbers)
    except Exception:
        return 0
