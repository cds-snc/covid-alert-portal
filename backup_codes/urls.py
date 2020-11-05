from django.urls import path

from . import views


urlpatterns = [
    path(
        "backup-codes",
        views.BackupCodeListView.as_view(),
        name="backup_codes",
    )
]
