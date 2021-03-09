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

location_choices = [
    ("restaurant_bar_coffee", _("Restaurant, bar, coffee shop")),
    ("fitness_recreation", _("Fitness and recreation")),
    ("arts_entertainment", _("Arts and entertainment")),
    ("grooming_wellness", _("Grooming and wellness")),
    ("religious_space", _("Religious space")),
    ("other", _("Something else")),
]


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

    category = forms.ChoiceField(
        label="",
        choices=location_choices,
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
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


class LocationUnavailableForm(HealthcareBaseForm, forms.Form):
    """
    A form to show a detour to unavailable locations.
    """

    pass


class ContactUsForm(HealthcareBaseForm, forms.Form):
    help_category = forms.ChoiceField(
        label="",
        choices=[
            ("get_help", _("Get Help.")),
            ("give_feedback", _("Give Feedback.")),
            ("something_else", _("Something Else.")),
        ],
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
    more_info = forms.CharField(
        label=_("Tell us more about the issue"),
        widget=forms.Textarea,
    )
    contact_email = forms.EmailField(
        label=_("Email address if you want a reply"),
        help_text=_(
            "We'll use this if we need to contact you. We will not use your email address for anything else."
        ),
        required=False,
    )
