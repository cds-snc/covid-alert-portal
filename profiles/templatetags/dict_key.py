from django.template.defaultfilters import register


@register.filter
def dict_key(d, k):
    """Returns the given key from a dictionary."""
    return d.get(k, "")
