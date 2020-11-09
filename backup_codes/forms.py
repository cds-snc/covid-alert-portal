from django import forms
from django.conf import settings
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient

class BackupCodesBaseForm(forms.Form):
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        # Remove the colon after field labels
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

        # override field attributes: https://stackoverflow.com/a/56870308
        for field in self.fields:
            self.fields[field].widget.attrs.pop("autofocus", None)
            # remove autocomplete attributes
            self.fields[field].widget.attrs.update({"autocomplete": "off"})

class RequestBackupCodesForm(BackupCodesBaseForm):
    def __init__(self, user, admin, *args, **kwargs):
        self.user = user
        self.admin = admin
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if self.user is None or self.user.is_authenticated is False:
            return False    

        return True
        
    def send_mail(
        self,
        language
    ):
        notifications_client = NotificationsAPIClient(
            settings.NOTIFY_API_KEY, base_url=settings.NOTIFY_ENDPOINT
        )

        try:
            notifications_client.send_email_notification(
                email_address=self.admin.email,
                template_id=settings.BACKUP_CODE_ADMIN_EMAIL_TEMPLATE_ID.get(
                    language or "en"
                ),
                personalisation={
                    "name": self.admin.name,
                    "user_email": self.user.email,
                    "user_name": self.user.name
                },
            )
        except HTTPError as e:
            raise Exception(e)