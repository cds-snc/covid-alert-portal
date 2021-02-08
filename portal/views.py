from django.shortcuts import render
from django.utils.translation import LANGUAGE_SESSION_KEY, check_for_language
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import translate_url
from urllib.parse import unquote, urlparse


def permission_denied_view(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def internal_error(request):
    return render(request, "500.html", status=500)


def switch_language(request):
    current_lang = request.LANGUAGE_CODE
    lang = "en"
    if current_lang == "en":
        lang = "fr"

    if check_for_language(lang) is False:
        # Make sure the lang has been enabled in the config. If not, default to en
        lang = "en"

    # Take the referer by default
    next_url = urlparse(request.META.get("HTTP_REFERER"))
    # but if a ?next_url has been provided, let's make sure it's clean

    next_url = next_url.path and unquote(next_url.path)
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        # if it is not clean, let's default to /
        next_url = "/"

    root_domain = ""
    if settings.URL_DUAL_DOMAINS:
        root_domain = (
            settings.URL_FR_PRODUCTION if lang == "fr" else settings.URL_EN_PRODUCTION
        )

    next_url = root_domain + translate_url(next_url, lang)
    response = HttpResponseRedirect(next_url)

    if hasattr(request, "session"):
        request.session[LANGUAGE_SESSION_KEY] = lang

    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response
