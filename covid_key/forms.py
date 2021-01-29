from django import forms
from django.conf import settings
from datetime import datetime

from phonenumber_field.formfields import PhoneNumberField

from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService
from portal.forms import HealthcareBaseForm
from portal.widgets import CDSRadioWidget


class OtkSmsForm(HealthcareBaseForm):
    """
    A form to specify patient phone number for receiving one time key (otk) by SMS
    """

    error_messages = {
        "phone_number2": _("Phone numbers must match"),
    }

    phone_number = PhoneNumberField(
        label=_("Enter patient’s mobile phone number"), max_length=100
    )
    phone_number2 = PhoneNumberField(label=_("Enter the number again"), max_length=100)

    def clean(self):
        super().clean()
        if (
            "phone_number" in self.cleaned_data
            and self.cleaned_data["phone_number"] != self.cleaned_data["phone_number2"]
        ):
            raise ValidationError(
                {"phone_number2": [self.error_messages["phone_number2"]]}
            )
        return self.cleaned_data

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
            details={"code": otk["code"]},
        )


class OtkSmsSentForm(HealthcareBaseForm):
    """
    A form for redirecting users after sending OTK via SMS
    """

    redirect_choice = forms.ChoiceField(
        label="",
        choices=[
            ("start", _("Yes, generate a key for another patient.")),
            ("otk_sms", _("No, try again or use different phone number.")),
            ("key", _("No, read key.")),
        ],
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
