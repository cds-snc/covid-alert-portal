from django import forms
from django.conf import settings
from datetime import datetime

from phonenumber_field.formfields import PhoneNumberField

from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService


class OtkSmsForm(forms.Form):
    """
    A form to specify patient phone number for receiving one time key (otk) by SMS
    """

    phone_number = PhoneNumberField(
        label="Enter patient's mobile phone number", max_length=100
    )
    phone_number2 = PhoneNumberField(
        label="Confirm patient's mobile phone number", max_length=100
    )

    @inject
    def send_sms(
        self,
        language,
        otk,
        notify_service: NotifyService = Provide[Container.notify_service],
    ):
        notify_service.send_sms(
            phone_number=str(self.cleaned_data.get("phone_number")),
            template_id=settings.OTK_SMS_TEMPLATE_ID.get(language or "en"),
            details={
                "code": otk["code"],
                "expiry": datetime.fromtimestamp(otk["expiry"]).strftime(
                    "%b %d %Y %H:%M:%S"
                ),
            },
        )
