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
from .widgets import AutocompleteWidget

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
        label=_("Email address if you want a reply"),
        help_text=_(
            "We'll use this if we need to contact you. We will not use your email address for anything else."
        ),
        required=False,
    )

    @inject
    def send_mail(
        self,
        subject_type,
        message,
        from_email,
        notify_service: NotifyService = Provide[Container.notify_service],
    ):
        notify_service.send_email(
            address=self.cleaned_data.get("contact_email"),
            template_id=settings.ISED_TEMPLATE_ID,
            details={
                "subject_type": subject_type,
                "message": message,
                "from_email": from_email,
            },
        )
