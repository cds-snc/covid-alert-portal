from django import template

register = template.Library()


@register.filter
def form_date(form, **kwargs):
    data = form.initial
    return "{}-{:02d}-{:02d}".format(
        data.get(f"year", 0), data.get(f"month", 0), data.get(f"day", 0)
    )
