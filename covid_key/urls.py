from django.urls import path
from django.views.generic import TemplateView
from django_otp.decorators import otp_required
from django.contrib.auth.views import login_required

from . import views

urlpatterns = [
    path("key/", views.code, name="key"),
    path(
        "start/",
        login_required(
            otp_required(TemplateView.as_view(template_name="covid_key/start.html"))
        ),
        name="start",
    ),
]
