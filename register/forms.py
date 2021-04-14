from django import forms

from portal.forms import HealthcareBaseForm
from django.utils.translation import gettext_lazy as _
from portal.widgets import CDSRadioWidget
from phonenumber_field.formfields import PhoneNumberField
from dependency_injector.wiring import inject, Provide
from portal.containers import Container
from portal.services import NotifyService
from .widgets import AutocompleteWidget, PhoneExtensionWidget


location_choices = [
    ("restaurant_bar_coffee", _("Restaurant, bar, coffee shop")),
    ("fitness_recreation", _("Fitness and recreation")),
    ("arts_entertainment", _("Arts and entertainment")),
    ("grooming_wellness", _("Grooming and wellness")),
    ("religious_space", _("Religious space")),
    ("events", _("Events, for example festivals or funerals.")),
    ("other", _("Something else")),
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
    email = forms.EmailField(label=_("Email address"))


class OtherFieldInput(HealthcareBaseForm, forms.Form):
    data = forms.CharField(label=_("Give brief description of service or event"))


class LocationCategoryForm(HealthcareBaseForm, forms.Form):
    category = forms.ChoiceField(
        label="",
        choices=location_choices,
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
    category_description = forms.CharField(
        label="Give brief description of service or event", required=False
    )

    def __init__(self, data=None, *args, **kwargs):
        super(LocationCategoryForm, self).__init__(data, *args, **kwargs)
        # If 'something else' is chosen, set category_description as required
        if data and data.get("category-category", None) == "other":
            self.fields["category_description"].required = True


class LocationNameForm(HealthcareBaseForm, forms.Form):
    name = forms.CharField(label="")


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
    address = forms.CharField(label=_("Address line 1"), widget=AutocompleteWidget())
    address_2 = forms.CharField(label=_("Address line 2"), required=False)
    city = forms.CharField(label=_("City"))
    province = forms.ChoiceField(label=_("Province or territory"), choices=provinces)
    postal_code = forms.CharField(label=_("Postal code"))


class LocationContactForm(HealthcareBaseForm, forms.Form):
    contact_name = forms.CharField(label=_("Name of contact"))
    contact_email = forms.EmailField(label=_("Contact email"))
    contact_phone = PhoneNumberField(label=_("Contact phone number"))
    contact_phone_ext = forms.CharField(
        label=_("Extension"), required=False
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
