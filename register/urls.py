from django.urls import path

from . import views

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
]
