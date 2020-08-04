from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def get_setting(setting):
    return getattr(settings, setting, None)
