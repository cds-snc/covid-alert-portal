from django.conf import settings
from django.dispatch import Signal
from invitations.adapters import BaseInvitationsAdapter

from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService

user_signed_up = Signal(providing_args=["request", "user"])


class HealthcareInvitationAdapter(BaseInvitationsAdapter):
    def get_user_signed_up_signal(self):
        return user_signed_up

    @inject
    def send_mail(
        self,
        template_prefix,
        email,
        context,
        notify_service: NotifyService = Provide[Container.notify_service],
    ):
        notify_service.send_email(
            address=context.get("email"),
            template_id=settings.INVITATION_EMAIL_TEMPLATE_ID.get(
                context.get("language") or "en"
            ),
            details={
                "url": context.get("invite_url"),
                "admin_email": context.get("inviter").email,
            },
        )
