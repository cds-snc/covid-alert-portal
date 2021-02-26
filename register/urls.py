from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views
from .forms import (
    LocationCategoryForm,
    LocationNameForm,
    LocationAddressForm,
    LocationContactForm,
    RegisterSummaryForm,
)

app_name = "register"

named_location_forms = (
    ("category", LocationCategoryForm),
    ("name", LocationNameForm),
    ("address", LocationAddressForm),
    ("contact", LocationContactForm),
    ("summary", RegisterSummaryForm),
)

location_wizard = views.LocationWizard.as_view(
    named_location_forms,
    url_name="register:location_step",
    done_step_name="confirmation",
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="register/start.html"), name="start"),
    path("email", views.RegistrantEmailView.as_view(), name="registrant_email"),
    path(
        "email/submitted",
        views.RegistrantEmailSubmittedView.as_view(),
        name="email_submitted",
    ),
    path(
        "email/<uuid:pk>/confirm",
        views.confirm_email,
        name="email_confirm",
    ),
    path(
        "email/confirm/error",
        TemplateView.as_view(template_name="register/error.html"),
        name="confirm_email_error",
    ),
    path("<uuid:pk>/name", views.RegistrantNameView.as_view(), name="registrant_name"),
    re_path(
        r"^(?P<pk>.+)/location/(?P<step>.+)/$", location_wizard, name="location_step"
    ),
    path("<uuid:pk>/location/", location_wizard, name="location"),
    path(
        "<uuid:pk>/confirmation",
        views.RegisterConfirmationPageView.as_view(),
        name="confirmation",
    ),
]
