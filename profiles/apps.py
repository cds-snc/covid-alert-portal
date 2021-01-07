from django.apps import AppConfig
from portal import container


class ProfilesConfig(AppConfig):
    name = "profiles"

    def ready(self):
        import profiles.signals  # noqa

        """
        Wire the dependency-injector.
        Each application must add this code in the apps.py file
        and list each module that uses dependency-injections
        """
        from . import forms
        from .utils import invitation_adapter

        container.wire(modules=[forms, invitation_adapter])
