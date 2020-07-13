from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import TemplateView

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
