from django.urls import re_path
from . import views

app_name = "announcements"

urlpatterns = [
    re_path(
        r"^(?P<pk>\d+)/hide/$",
        views.AnnouncementDismissView.as_view(),
        name="dismiss",
    )
]
