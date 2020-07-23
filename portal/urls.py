from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns

from django.utils.translation import gettext_lazy as _lz

from .admin import Admin2FASite

admin.site.__class__ = Admin2FASite
admin.site.site_header = _lz("COVID Health portal")

urlpatterns = [
    re_path(
        r"^robots.txt",
        lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"),
        name="robots_file",
    ),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", include("profiles.urls")),
    path("invitations/", include("invitations.urls", namespace="invitations"),),
)
