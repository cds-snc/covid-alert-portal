from django import template
from django.conf import settings
from django.utils.html import format_html
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def lang_switch(context, lang):
    path = context.get("request").get_full_path()
    if not settings.URL_DUAL_DOMAINS:
        return format_html(
            '<a role="button" href="{}" onclick="document.forms["language_toggle"].submit();">{}</a>',
            translate_url(path, lang.get("code")),
            lang.get("name_local"),
        )
    elif lang.get("code") == "en":
        return format_html(
            '<a role="button" href="{}">{}</a>',
            settings.URL_EN_PRODUCTION + translate_url(path, lang.get("code")),
            lang.get("name_local"),
        )
    else:
        return format_html(
            "<a role='button' href='{}'>{}</a>",
            settings.URL_FR_PRODUCTION + translate_url(path, lang.get("code")),
            lang.get("name_local"),
        )
