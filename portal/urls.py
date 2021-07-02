from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from axes.admin import AccessLogAdmin
from invitations.views import AcceptInvite

from .admin import Admin2FASite
from . import views

admin.site.__class__ = Admin2FASite
admin.site.site_header = (
    "COVID Health Portal administration | Administration du Portail Alerte COVID"
)
admin.site.site_title = admin.site.site_header


def disable_delete_permissions(cls, request, obj=None):
    return False


AccessLogAdmin.has_delete_permission = disable_delete_permissions

handler403 = views.permission_denied_view
handler404 = views.page_not_found
handler500 = views.internal_error

# ----
# URL paths shared among all apps
# ----
urlpatterns = [
    re_path(
        r"^robots.txt",
        lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"),
        name="robots_file",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("403/", views.permission_denied_view),
    path("404/", views.page_not_found),
    path("500/", views.internal_error),
    path(
        "switch-language/",
        views.switch_language,
        name="switch_language",
    ),
]

# ----
# URL paths used when serving the OTK Portal site
# ----
if settings.APP_SWITCH == "PORTAL" or settings.APP_SWITCH == "UNIT":
    invitation_patterns = (
        [
            # https://github.com/bee-keeper/django-invitations/blob/master/invitations/urls.py
            re_path(
                r"^accept-invite/(?P<key>\w+)/?$",
                AcceptInvite.as_view(),
                name="accept-invite",
            ),
        ],
        "invitations",
    )

    urlpatterns += [
        path("admin/", admin.site.urls),
    ]

    urlpatterns += i18n_patterns(
        path("", include("profiles.urls")),
        path("", include("covid_key.urls")),
        path("contact/", include("contact.urls")),
        path("about/", include("about.urls")),
        path("outbreaks/", include("outbreaks.urls")),
        path("", include("backup_codes.urls")),
        path(
            "invitations/",
            include(invitation_patterns, namespace="invitations"),
        ),
        path("announcements/", include("announcements.urls")),
    )

# ----
# URL Paths used when serving the QR Code registration site
# ----
if settings.APP_SWITCH == "QRCODE":
    urlpatterns += i18n_patterns(
        path("", include("register.urls")),
        path("contact/", include("contact.urls")),
    )

if settings.APP_SWITCH == "UNIT":
    urlpatterns += i18n_patterns(
        path("register", include("register.urls")),
    )
