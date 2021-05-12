from django import template
from django.conf import settings
register = template.Library()

@register.simple_tag
def get_ga_id():
    return settings.GA_ID