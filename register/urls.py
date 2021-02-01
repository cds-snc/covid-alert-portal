from django.urls import path, re_path

from . import views
from .forms import (
    LocationCategoryForm,
    LocationNameForm,
    LocationAddressForm,
    LocationContactForm,
)

app_name = "register"

named_location_forms = (
    ("category", LocationCategoryForm),
    ("name", LocationNameForm),
    ("address", LocationAddressForm),
    ("contact", LocationContactForm),
)

location_wizard = views.LocationWizard.as_view(
    named_location_forms, url_name="register:location_step", done_step_name="summary"
)

urlpatterns = [
    path("", views.RegisterStartPageView.as_view(), name="start"),
    path("email", views.RegistrantEmailView.as_view(), name="email"),
    path("<uuid:pk>/name", views.RegistrantNameView.as_view(), name="name"),
    re_path(
        r"^(?P<pk>.+)/location/(?P<step>.+)/$", location_wizard, name="location_step"
    ),
    path("<uuid:pk>/location/", location_wizard, name="location"),
    path("<uuid:pk>/summary", views.RegisterSummaryPageView.as_view(), name="summary"),
    path(
        "confirmation",
        views.RegisterConfirmationPageView.as_view(),
        name="confirmation",
    ),
]
