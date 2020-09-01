from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns
from axes.admin import AccessLogAdmin
from invitations.views import AcceptInvite

from .admin import Admin2FASite

admin.site.__class__ = Admin2FASite
admin.site.site_header = (
    "COVID Health Portal administration | Administration du Portail Alerte COVID"
)
admin.site.site_title = admin.site.site_header


def disable_delete_permissions(cls, request, obj=None):
    return False


AccessLogAdmin.has_delete_permission = disable_delete_permissions

urlpatterns = [
    re_path(
        r"^robots.txt",
        lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"),
        name="robots_file",
    ),
    path(
        r"status/",
        lambda x: HttpResponse("Ok", content_type="text/plain"),
        name="status",
    ),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

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

urlpatterns += i18n_patterns(
    path("", include("profiles.urls")),
    path("", include("covid_key.urls")),
    path("contact/", include("contact.urls")),
    path("invitations/", include(invitation_patterns, namespace="invitations"),),
)
