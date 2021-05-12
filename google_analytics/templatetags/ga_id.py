from django import template
from django.conf import settings
register = template.Library()

if settings.GA_ID:
    template = "includes/google_analytics.html"
else:
    template = None

@register.inclusion_tag(template)
def get_ga_script():
    return

@register.simple_tag
def get_ga_id():
    return settings.GA_ID