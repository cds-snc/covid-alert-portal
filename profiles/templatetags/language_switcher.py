from django import template
from django.conf import settings
from django.urls import translate_url

register = template.Library()


@register.simple_tag()
def get_lang_title(lang, langEn, langFr):
    if lang == "en":
        return langFr.get("name_local").title()
    else:
        return langEn.get("name_local").title()


@register.simple_tag(takes_context=True)
def get_href(context, lang):
    path = context.get("request").get_full_path()
    root_domain = ""
    translated_lang = "fr" if lang == "en" else "en"

    if settings.URL_DUAL_DOMAINS:
        root_domain = (
            settings.URL_FR_PRODUCTION
            if translated_lang == "fr"
            else settings.URL_EN_PRODUCTION
        )

    return root_domain + translate_url(path, translated_lang)
