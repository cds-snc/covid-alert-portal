from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.views import PasswordResetView
from django_otp.views import LoginView
from django.contrib.auth import views as login_views

from . import views
from . import forms


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login")),
    path("invite/", views.InvitationView.as_view(), name="invite"),
    path("invite/list/", views.InvitationListView.as_view(), name="invitation_list"),
    path(
        "invite/<int:pk>/delete",
        views.InvitationDeleteView.as_view(),
        name="invitation_delete",
    ),
    path(
        "invite-complete/",
        views.InvitationCompleteView.as_view(),
        name="invite_complete",
    ),
    re_path(r"signup/$", views.SignUpView.as_view(), name="signup"),
    path("profiles/", views.ProfilesView.as_view(), name="profiles",),
    path("profiles/<uuid:pk>", views.UserProfileView.as_view(), name="user_profile",),
    path(
        "profiles/<uuid:pk>/delete", views.UserDeleteView.as_view(), name="user_delete",
    ),
    path(
        "profiles/<uuid:pk>/edit/name",
        views.HealthcareUserEditView.as_view(
            form_class=forms.HealthcareNameEditForm,
            template_name=forms.HealthcareNameEditForm.template_name,
        ),
        name="user_edit_name",
    ),
    path(
        "profiles/<uuid:pk>/edit/phone",
        views.HealthcareUserEditView.as_view(
            form_class=forms.HealthcarePhoneEditForm,
            template_name=forms.HealthcarePhoneEditForm.template_name,
        ),
        name="user_edit_phone",
    ),
    path(
        "profiles/<uuid:pk>/edit/password",
        views.HealthcareUserEditView.as_view(
            form_class=forms.HealthcarePasswordEditForm,
            template_name=forms.HealthcarePasswordEditForm.template_name,
        ),
        name="user_edit_password",
    ),
    path(
        "profiles/<uuid:pk>/edit/email",
        views.HealthcareUserEditView.as_view(
            form_class=forms.HealthcareEmailEditForm,
            template_name=forms.HealthcareEmailEditForm.template_name,
        ),
        name="user_edit_email",
    ),
    path(
        "login/",
        LoginView.as_view(authentication_form=forms.HealthcareAuthenticationForm),
        name="login",
    ),
    path("login-2fa/", views.Login2FAView.as_view(), name="login-2fa",),
    path("resend-2fa/", views.Resend2FAView.as_view(), name="resend-2fa",),
    path(
        "session-timed-out/", views.redirect_after_timed_out, name="session_timed_out"
    ),
    path(
        "privacy/",
        TemplateView.as_view(template_name="profiles/privacy.html"),
        name="privacy",
    ),
]

# The PasswordResetView doesn't have any html template by default
PasswordResetView.html_email_template_name = (
    "registration/password_reset_email_html.html"
)
# Django.contrib.auth urls have underscore in them, let's change that for dashes
urlpatterns += [
    path(
        "password-change/",
        login_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password-change/done/",
        login_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password-reset/done/",
        login_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/",
        PasswordResetView.as_view(form_class=forms.HealthcarePasswordResetForm),
        name="password_reset",
    ),
    path(
        "reset/<uidb64>/<token>/",
        login_views.PasswordResetConfirmView.as_view(
            post_reset_login=True, post_reset_login_backend="axes.backends.AxesBackend",
        ),
        name="password_reset_confirm",
    ),
    path("reset/done/", views.password_reset_complete, name="password_reset_complete"),
    # If this doesnt go last, I can't overwrite the handler for the urls.
    path("", include("django.contrib.auth.urls")),
]
