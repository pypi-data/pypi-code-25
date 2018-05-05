from django import template


register = template.Library()


@register.filter
def elem(value, obj):
    try:
        return value.get(obj)
    except AttributeError:
        return value[obj]


@register.filter
def divide(value, divisor):
    return int(value/divisor)
