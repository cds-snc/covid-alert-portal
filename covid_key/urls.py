from django.urls import path

from . import views

urlpatterns = [
    path("key/", views.code, name="key"),
]
