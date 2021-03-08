from django import template

register = template.Library()


@register.filter
def fieldset_date(fieldset, **kwargs):
    i = fieldset.title.split("_")[1]
    data = fieldset.form.initial
    return "{}-{:02d}-{:02d}".format(
        data.get(f"year_{i}", 0), data.get(f"month_{i}", 0), data.get(f"day_{i}", 0)
    )
