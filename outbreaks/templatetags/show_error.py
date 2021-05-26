from django import template

register = template.Library()


@register.filter
def show_error(dictionary):
    try:
        return list(dictionary.data[0])[0]
    except (TypeError, IndexError, AttributeError):
        return ""
