from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views
from .forms import (
    LocationCategoryForm,
    LocationNameForm,
    LocationAddressForm,
    LocationContactForm,
    RegisterSummaryForm,
    forms,
)

from register.views import check_for_province

app_name = "register"


# order matters here
named_location_forms = (
    ("category", LocationCategoryForm),
    ("name", LocationNameForm),
    ("address", LocationAddressForm),
    ("unavailable", forms.Form),
    ("contact", LocationContactForm),
    ("summary", RegisterSummaryForm),
)

location_wizard = views.LocationWizard.as_view(
    named_location_forms,
    url_name="register:location_step",
    done_step_name="confirmation",
    condition_dict={"unavailable": check_for_province},
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="register/start.html"), name="start"),
    path("email", views.RegistrantEmailView.as_view(), name="registrant_email"),
    path(
        "locations/<uuid:pk>/poster/<str:lang>",
        views.download_poster,
        name="poster_download",
    ),
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
    re_path(r"^location/(?P<step>.+)/$", location_wizard, name="location_step"),
    path("location/", location_wizard, name="location"),
    path(
        "confirmation",
        views.RegisterConfirmationPageView.as_view(),
        name="confirmation",
    ),
    path("contactus", views.ContactUsPageView.as_view(), name="contactus"),
    path("help", views.HelpPageView.as_view(), name="help"),
    path(
        "display",
        TemplateView.as_view(template_name="register/how_display_poster.html"),
        name="howtodisplay",
    ),
    path(
        "success",
        TemplateView.as_view(template_name="register/success.html"),
        name="success",
    ),
]
