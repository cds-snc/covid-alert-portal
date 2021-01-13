from django.apps import AppConfig
from portal import container


class CovidKeyConfig(AppConfig):
    name = "covid_key"

    def ready(self):
        """
        Wire the dependency-injector.
        Each application must add this code in the apps.py file
        and list each module that uses dependency-injections
        """
        from . import forms

        container.wire(modules=[forms])
