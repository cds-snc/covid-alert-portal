from django.apps import AppConfig


class BackupCodesConfig(AppConfig):
    name = "backup_codes"

    def ready(self):
        import backup_codes.signals  # noqa
