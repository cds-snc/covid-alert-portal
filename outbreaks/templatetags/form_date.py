from django import template

register = template.Library()


@register.filter
def form_date(form, **kwargs):
    data = form.initial
    return "{}-{:02d}-{:02d}".format(
        data.get("year", 0), data.get("month", 0), data.get("day", 0)
    )
