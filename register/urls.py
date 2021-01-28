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
    path("create", views.RegistrantCreate.as_view(), name="create"),
    path("<uuid:pk>/name", views.RegistrantUpdate.as_view(), name="name"),
]
