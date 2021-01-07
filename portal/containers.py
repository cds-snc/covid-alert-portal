"""
Containers module for the dependency-injection package
"""

from dependency_injector import containers, providers
from .services import NotifyService


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    notify_service = providers.Singleton(
        NotifyService, api_key=config.NOTIFY_API_KEY, end_point=config.NOTIFY_ENDPOINT
    )
