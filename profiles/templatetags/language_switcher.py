from django import template

register = template.Library()


@register.simple_tag()
def get_lang_title(lang, langEn, langFr):
    if lang == "en":
        return langFr.get("name_local").title()
    else:
        return langEn.get("name_local").title()
