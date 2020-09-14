from django.conf import settings
from invitations.adapters import BaseInvitationsAdapter

from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient


class HealthcareInvitationAdapter(BaseInvitationsAdapter):
    def send_mail(self, template_prefix, email, context):
        notifications_client = NotificationsAPIClient(
            settings.NOTIFY_API_KEY, base_url=settings.NOTIFY_ENDPOINT
        )

        try:
            notifications_client.send_email_notification(
                email_address=context.get("email"),
                template_id=settings.INVITATION_EMAIL_TEMPLATE_ID.get(
                    context.get("language") or "en"
                ),
                personalisation={
                    "url": context.get("invite_url"),
                },
            )
        except HTTPError as e:
            raise Exception(e)
