from django import template

register = template.Library()


@register.filter(name='average')
def average(iterable, attr=None):
    """Return the average of values in an iterable.

    Usage in template:
        {{ queryset|average:"field_name" }}
    or for list of numbers:
        {{ numbers|average }}
    """
    try:
        if iterable is None:
            return 0

        # If attr passed, extract attribute or dict key
        values = []
        if attr:
            for item in iterable:
                # support dict-like and object attribute access
                try:
                    val = getattr(item, attr)
                except Exception:
                    try:
                        val = item.get(attr)
                    except Exception:
                        val = None
                if val is not None:
                    try:
                        values.append(float(val))
                    except Exception:
                        continue
        else:
            for item in iterable:
                try:
                    values.append(float(item))
                except Exception:
                    continue

        if not values:
            return 0

        return sum(values) / len(values)
    except Exception:
        return 0
from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def average(queryset, field_name):
    if not queryset:
        return 0
    return queryset.aggregate(avg=Avg(field_name))['avg'] or 0
