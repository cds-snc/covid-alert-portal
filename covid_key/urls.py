from django.urls import path

from . import views

urlpatterns = [
    path("key/", views.code, name="key"),
    path("key-instructions/", views.code, name="key_instructions"),
]
