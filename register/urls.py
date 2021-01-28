from django.urls import path

from .views import RegisterStartPageView

app_name = "register"

urlpatterns = [
    path("", RegisterStartPageView.as_view(), name="start"),
]