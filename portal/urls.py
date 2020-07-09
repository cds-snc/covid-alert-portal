from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    re_path(
        r"^robots.txt",
        lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"),
        name="robots_file",
    ),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    re_path(r"session_security/", include("session_security.urls")),
]

urlpatterns += i18n_patterns(
    path("", include("profiles.urls")),
    re_path(r"^invitations/", include("invitations.urls", namespace="invitations")),
)
