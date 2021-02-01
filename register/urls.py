from django.urls import path

from . import views
from .forms import LocationCategoryForm, LocationNameForm

app_name = "register"

urlpatterns = [
    path("", views.RegisterStartPageView.as_view(), name="start"),
    path(
        "confirmation",
        views.RegisterConfirmationPageView.as_view(),
        name="confirmation",
    ),
    path("email", views.RegistrantEmailView.as_view(), name="email"),
    path("<uuid:pk>/name", views.RegistrantNameView.as_view(), name="name"),
    path("<uuid:pk>/location", views.LocationWizard.as_view(views.FORMS)),
]
