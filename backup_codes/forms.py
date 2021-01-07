from django.conf import settings
from portal.forms import HealthcareBaseForm
from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService


class RequestBackupCodesForm(HealthcareBaseForm):
    def __init__(self, user, admin, *args, **kwargs):
        self.user = user
        self.admin = admin
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if self.user is None or self.user.is_authenticated is False:
            return False

        return True

    @inject
    def send_mail(
        self,
        language,
        notify_service: NotifyService = Provide[Container.notify_service],
    ):
        notify_service.send_email(
            address=self.admin.email,
            template_id=settings.BACKUP_CODE_ADMIN_EMAIL_TEMPLATE_ID.get(
                language or "en"
            ),
            details={
                "name": self.admin.name,
                "user_email": self.user.email,
                "user_name": self.user.name,
            },
        )
