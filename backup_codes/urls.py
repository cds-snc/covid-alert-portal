from django.urls import path
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path(
        "backup-codes",
        views.BackupCodeListView.as_view(),
        name="backup_codes",
    ),
    path(
        "backup-codes-help",
        views.RequestBackupCodes.as_view(),
        name="backup_codes_help",
    ),
    path(
        "backup-codes-contacted",
        TemplateView.as_view(template_name="backup_codes/backup_codes_contacted.html"),
        name="backup_codes_contacted",
    ),
]
