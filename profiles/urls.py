from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.views import PasswordResetView, login_required
from django_otp.views import LoginView
from django_otp.decorators import otp_required

from . import views
from . import forms

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="landing")),
    path(
        "landing/",
        TemplateView.as_view(template_name="profiles/landing.html"),
        name="landing",
    ),
    # The otp_required is used directly in the view in this case
    path("code/", views.code, name="code"),
    path(
        "start/",
        login_required(
            otp_required(TemplateView.as_view(template_name="profiles/start.html"))
        ),
        name="start",
    ),
    path("invite/", views.InviteView.as_view(), name="invite"),
    path(
        "invite_complete/", views.InviteCompleteView.as_view(), name="invite_complete"
    ),
    re_path(r"signup/$", views.SignUpView.as_view(), name="signup"),
    path("profiles/", views.ProfilesView.as_view(), name="profiles",),
    re_path(
        r"profiles/(?P<pk>\w+)$", views.UserProfileView.as_view(), name="user_profile",
    ),
    re_path(
        r"profiles/(?P<pk>\w+)/delete$",
        views.UserDeleteView.as_view(),
        name="user_delete",
    ),
    # Removed for now
    # url(r'profiles/(?P<pk>\w+)/edit$', views.UserEdit.as_view(), name='user_edit'),
    # this login path overrides the default one in 'django.contrib.auth.urls'
    path(
        "login/",
        LoginView.as_view(authentication_form=forms.HealthcareAuthenticationForm),
        name="login",
    ),
    path("login-2fa/", views.Login2FAView.as_view(), name="login-2fa",),
    path("resend-2fa/", views.Resend2FAView.as_view(), name="resend-2fa",),
    path(
        "password_reset/",
        PasswordResetView.as_view(form_class=forms.HealthcarePasswordResetForm),
        name="password_reset",
    ),
    path(
        "privacy/",
        TemplateView.as_view(template_name="profiles/privacy.html"),
        name="privacy",
    ),
    path("", include("django.contrib.auth.urls")),
]
