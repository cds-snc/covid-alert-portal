from django.urls import path
from . import views


app_name = "outbreaks"
urlpatterns = [
    path(
        "",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "<uuid:pk>/profile",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "datetime",
        views.DatetimeView.as_view(),
        name="datetime",
    ),
    path(
        "severity",
        views.SeverityView.as_view(),
        name="severity",
    ),
    path(
        "confirm",
        views.ConfirmView.as_view(),
        name="confirm",
    ),
    path(
        "confirmed",
        views.ConfirmedView.as_view(),
        name="confirmed",
    ),
    path(
        "history",
        views.HistoryView.as_view(),
        name="history",
    ),
    path(
        "<uuid:pk>/details",
        views.ExposureDetailsView.as_view(),
        name="details",
    ),
]
