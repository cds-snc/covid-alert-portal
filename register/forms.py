from django import forms
from django.conf import settings

from portal.forms import HealthcareBaseForm
from django.utils.translation import gettext_lazy as _
from .models import Registrant
from portal.widgets import CDSRadioWidget
from phonenumber_field.formfields import PhoneNumberField
from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService


class EmailForm(HealthcareBaseForm, forms.Form):
    email = forms.EmailField(label=_("Email address"))

    @inject
    def send_mail(
        self,
        language,
        to_email,
        link,
        notify_service: NotifyService = Provide[Container.notify_service],
    ):
        notify_service.send_email(
            address=to_email,
            template_id=settings.REGISTER_EMAIL_CONFIRMATION_ID.get(language or "en"),
            details={"verification_link": link},
        )


class RegistrantNameForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Registrant

        fields = ("name",)


class LocationCategoryForm(HealthcareBaseForm, forms.Form):
    help_text = {
        "arts_culture": "For example, cinemas, museums, and art galleries",
        "community": "Both public or private daycare",
        "fitness": "For example, schools and universities",
        "food_service": "For example, hospitals and family practices",
        "private_event": "Both essential and non-essential",
        "rental": "For example, hospitals and family practices",
        "retail": "What does this include in Canada?",
    }

    category = forms.ChoiceField(
        label="",
        choices=[
            ("arts_culture", _("Arts & culture")),
            ("community", _("Community spaces & libraries")),
            ("fitness", _("Fitness")),
            ("food_service", _("Food service & licensed establishments")),
            ("personal_care", _("Personal care services")),
            ("private_event", _("Private events/functions")),
            ("rental", _("Rented meeting, event & rehearsal spaces")),
            ("retail", _("Retail/shopping")),
            ("sports", _("Sports & recreation facilities")),
            ("other", _("Other")),
        ],
        widget=CDSRadioWidget(
            attrs={"class": "multichoice-radio", "help_text": help_text}
        ),
    )


class LocationNameForm(HealthcareBaseForm, forms.Form):
    name = forms.CharField(label="")


class LocationAddressForm(HealthcareBaseForm, forms.Form):
    address = forms.CharField(label=_("Address line 1"))
    address_2 = forms.CharField(label=_("Address line 2"), required=False)
    city = forms.CharField(label=_("City"))
    province = forms.CharField(label=_("Province or territory"))
    postal_code = forms.CharField(label=_("Postal code"))


class LocationContactForm(HealthcareBaseForm, forms.Form):
    contact_name = forms.CharField(label=_("Name of contact"))
    contact_email = forms.EmailField(label=_("Contact email"))
    contact_phone = PhoneNumberField(label=_("Contact phone number"))


class RegisterSummaryForm(HealthcareBaseForm, forms.Form):
    """
    A form to show an information panel.
    """

    pass
