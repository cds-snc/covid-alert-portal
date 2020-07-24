from django.urls import path

from . import views

urlpatterns = [
    # The otp_required is used directly in the view in this case
    path("key/", views.code, name="key"),
    path("key-instructions/", views.code, name="key_instructions"),
]
