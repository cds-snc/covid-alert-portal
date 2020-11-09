from django.urls import path

from . import views


urlpatterns = [
    path(
        "backup-codes",
        views.BackupCodeListView.as_view(),
        name="backup_codes",
    )
    ,
    path(
        "backup-codes-help",
        views.RequestBackupCodes.as_view(),
        name="backup_codes_help"
    )
]
