from django import template
from django.utils.translation import gettext_lazy as _
from ..forms import (
    type_establishment,
    type_event,
    type_event_or_establishment,
    location_category_type_map,
)

register = template.Library()


@register.simple_tag
def location_type_str(location_category, prefix, *args, **kwargs):
    """
    Returns whole string based on type of location, event or establishment
    """
    if location_category:
        if prefix == "address":
            if location_category_type_map[location_category] == type_establishment:
                return _("Address of establishment")
            elif location_category_type_map[location_category] == type_event:
                return _("Address of event")
            elif (
                location_category_type_map[location_category] == type_event_or_establishment
            ):
                return _("Address of establishment or event")
        elif prefix == "name":
            if location_category_type_map[location_category] == type_establishment:
                return _("Name of establishment")
            elif location_category_type_map[location_category] == type_event:
                return _("Name of event")
            elif (
                location_category_type_map[location_category] == type_event_or_establishment
            ):
                return _("Name of establishment or event")
        raise ValueError("Location category or prefix not valid for template tag filter.")
