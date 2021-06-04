from django.urls import path, re_path
from django.views.generic import TemplateView
from django_otp.decorators import otp_required
from django.contrib.auth.views import login_required

from . import views

urlpatterns = [
    path("key/", views.CodeView.as_view(), name="key"),
    path(
        "start/",
        login_required(otp_required(views.StartLandingView.as_view())),
        name="start",
    ),
    path(
        "otk-start/",
        login_required(otp_required(views.OTKStartView.as_view())),
        name="otk_start",
    ),
    path(
        "generate-key/",
        login_required(
            otp_required(
                TemplateView.as_view(template_name="covid_key/generate_key.html")
            )
        ),
        name="generate_key",
    ),
    path(
        "otk-sms/",
        login_required(otp_required(views.OtkSmsView.as_view())),
        name="otk_sms",
    ),
    re_path(
        r"otk_sms_sent/(?P<phone_number>[+\d]{0,50})$",
        login_required(otp_required(views.OtkSmsSentView.as_view())),
        name="otk_sms_sent",
    ),
]
