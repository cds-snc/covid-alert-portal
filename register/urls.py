from django.urls import path, re_path

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
    path("", views.RegisterStartPageView.as_view(), name="start"),
    path("email", views.RegistrantEmailView.as_view(), name="registrant_email"),
    path("<uuid:pk>/name", views.RegistrantNameView.as_view(), name="registrant_name"),
    re_path(
        r"^(?P<pk>.+)/location/(?P<step>.+)/$", location_wizard, name="location_step"
    ),
    path("<uuid:pk>/location/", location_wizard, name="location"),
    path(
        "confirmation",
        views.RegisterConfirmationPageView.as_view(),
        name="confirmation",
    ),
]
