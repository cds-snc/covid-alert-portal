from django import forms

from portal.forms import HealthcareBaseForm
from django.utils.translation import gettext_lazy as _
from portal.widgets import CDSRadioWidget
from phonenumber_field.formfields import PhoneNumberField
from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService
from .widgets import AutocompleteWidget

type_event = 1
type_establishment = 2
type_event_or_establishment = 3
location_restaurant_bar_coffee = "restaurant_bar_coffee"
location_fitness_recreation = "fitness_recreation"
location_arts_entertainment = "arts_entertainment"
location_grooming_wellness = "grooming_wellness"
location_religious_space = "religious_space"
location_events = "events"
location_other = "other"

location_category_type_map = {
    location_restaurant_bar_coffee: type_establishment,
    location_fitness_recreation: type_establishment,
    location_arts_entertainment: type_establishment,
    location_grooming_wellness: type_establishment,
    location_religious_space: type_establishment,
    location_events: type_event,
    location_other: type_event_or_establishment,
}

location_choices = [
    (location_restaurant_bar_coffee, _("Restaurant, bar, coffee shop")),
    (location_fitness_recreation, _("Fitness and recreation")),
    (location_arts_entertainment, _("Arts and entertainment")),
    (location_grooming_wellness, _("Grooming and wellness")),
    (location_religious_space, _("Religious space")),
    (location_events, _("Events, for example festivals or funerals.")),
    (location_other, _("Something else")),
]


@inject
def send_email(
    to_email,
    payload,
    template_id,
    notify_service: NotifyService = Provide[Container.notify_service],
):
    notify_service.send_email(
        address=to_email, template_id=template_id, details=payload
    )


class EmailForm(HealthcareBaseForm, forms.Form):
    email = forms.EmailField(label=_("Email address"), max_length=255)


class LocationCategoryForm(HealthcareBaseForm, forms.Form):
    category = forms.ChoiceField(
        label="",
        choices=location_choices,
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
    category_description = forms.CharField(
        label=_("Tell us the type of establishment."), required=False, max_length=200
    )

    def clean(self):
        cleaned_data = super().clean()
        other_selected = cleaned_data.get("category") == "other"
        category_description = cleaned_data.get("category_description")

        if other_selected and not category_description:
            raise forms.ValidationError(_("Tell us the type of establishment."))


class LocationNameForm(HealthcareBaseForm, forms.Form):
    name = forms.CharField(label="", max_length=65, error_messages={
        "max_length": _("Your name is longer than the %(limit_value)d character limit")
    })


provinces = [
    ("", _("Select a province or territory")),
    ("AB", _("Alberta")),
    ("BC", _("British Columbia")),
    ("MB", _("Manitoba")),
    ("NB", _("New Brunswick")),
    ("NL", _("Newfoundland and Labrador")),
    ("NS", _("Nova Scotia")),
    ("NT", _("Northwest Territories")),
    ("NU", _("Nunavut")),
    ("ON", _("Ontario")),
    ("PE", _("Prince Edward Island")),
    ("QC", _("Quebec")),
    ("SK", _("Saskatchewan")),
    ("YT", _("Yukon")),
]


class LocationAddressForm(HealthcareBaseForm, forms.Form):
    address = forms.CharField(
        label=_("Address line 1"), widget=AutocompleteWidget(), max_length=200
    )
    address_2 = forms.CharField(
        label=_("Address line 2"), required=False, max_length=200
    )
    city = forms.CharField(label=_("City"), max_length=100)
    province = forms.ChoiceField(label=_("Province or territory"), choices=provinces)
    postal_code = forms.CharField(label=_("Postal code"), max_length=10)


class LocationContactForm(HealthcareBaseForm, forms.Form):
    contact_name = forms.CharField(label=_("Name of contact"), max_length=200)
    contact_email = forms.EmailField(label=_("Contact email"), max_length=255)
    contact_phone = PhoneNumberField(
        label=_("Contact phone number"),
        error_messages={"invalid": _("Your phone number must have 10 digits")},
    )
    contact_phone_ext = forms.CharField(
        label=_("Extension"), required=False, max_length=20
    )


class RegisterSummaryForm(HealthcareBaseForm, forms.Form):
    """
    A form to show an information panel.
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
        label=_("Email address"),
        help_text=_(
            "We'll use this if we need to contact you. We will not use your email address for anything else."
        ),
    )
