from django.apps import AppConfig
from portal import container


class BackupCodesConfig(AppConfig):
    name = "backup_codes"

    def ready(self):
        import backup_codes.signals  # noqa

        """
        Wire the dependency-injector.
        Each application must add this code in the apps.py file
        and list each module that uses dependency-injections
        """
        from . import forms

        container.wire(modules=[forms])
