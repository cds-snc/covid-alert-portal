import logging
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError
from requests import post

from portal.forms import HealthcareBaseForm

logger = logging.getLogger(__name__)


class ContactForm(HealthcareBaseForm):
    name = forms.CharField(label=_("Your name"))
    email = forms.EmailField(
        label=_("Your email address"),
        error_messages={
            "required": _("Enter your email address if you want to contact us")
        },
    )
    FEEDBACK_MESSAGE = _("You need to tell us about your issue before you contact us")
    feedback = forms.CharField(
        label=_("Ask questions or give feedback"),
        error_messages={"required": FEEDBACK_MESSAGE},
        widget=forms.Textarea,
    )

    def send_freshdesk(self):
        try:
            response = post(
                settings.FRESHDESK_API_ENDPOINT + "/tickets",
                json={
                    "email": self.cleaned_data.get("email", None),
                    "subject": self.cleaned_data.get("feedback", "")[0:20] + "...",
                    "description": self.cleaned_data.get("feedback", ""),
                    "name": self.cleaned_data.get("name", ""),
                    "product_id": settings.FRESHDESK_PRODUCT_ID,
                    "status": 2,
                    "priority": 1,
                },
                auth=(settings.FRESHDESK_API_KEY, ""),
            )
            response.raise_for_status()
        except Exception as e:
            logger.critical(f"Unable to communicate with Freshdesk : {e}")
            raise ValidationError(
                _(
                    "There was a problem and your feedback wasn't submitted. Please email your feedback to assistance+healthcare@cds-snc.ca."
                )
            )
