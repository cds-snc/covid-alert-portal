from django.urls import path
from . import views


app_name = "exposure_notifications"
urlpatterns = [
    path(
        "",
        views.StartView.as_view(),
        name="start",
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
