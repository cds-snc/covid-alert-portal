from django import template
from profiles.utils import get_site_name

register = template.Library()


@register.simple_tag(takes_context=True)
def site_name(context):
    request = context.get("request")
    f = get_site_name(request) + ": "
    print(f)
    return f
