from django import template

register = template.Library()


@register.filter
def percentof(amount, total):
    try:
        return '{:.1f}%'.format(amount / total * 100)
    except ZeroDivisionError:
        return None
