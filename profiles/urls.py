from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.views import login_required, PasswordResetView, LoginView

from . import views
from . import forms

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="landing")),
    path(
        "landing/",
        TemplateView.as_view(template_name="profiles/landing.html"),
        name="landing",
    ),
    path("code/", views.code, name="code"),
    path(
        "start/",
        login_required(TemplateView.as_view(template_name="profiles/start.html")),
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
    path(
        "password_reset/",
        PasswordResetView.as_view(form_class=forms.HealthcarePasswordResetForm),
        name="password_reset",
    ),
    path("", include("django.contrib.auth.urls")),
]
