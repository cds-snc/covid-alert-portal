from django import forms

from portal.forms import HealthcareBaseForm
from django.utils.translation import gettext_lazy as _
from .models import Registrant, Location
from portal.widgets import CDSRadioWidget


class EmailForm(HealthcareBaseForm, forms.Form):
    email = forms.EmailField(label="Email address")


class RegistrantNameForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Registrant

        fields = ("name",)


class LocationCategoryForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Location
        fields = ("category",)

    category = forms.ChoiceField(
        label="",
        choices=[
            ("accommodation", _("Accommodation")),
            ("childcare", _("Childcare")),
            ("education", _("Education")),
            ("medical", _("Medical Facility")),
            ("restaurant", _("Restaurant, cafe, pub or bar")),
            ("retail", _("Retail store")),
            ("transport", _("Transport")),
            ("other", _("Other")),
        ],
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )


class LocationNameForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Location
        fields = ("name",)

    name = forms.CharField(
        label="What is the name of your business, organization or event?"
    )


class LocationAddressForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Location
        fields = ("address", "address_2", "city", "province", "postal_code")

    address = forms.CharField(label="Address line 1")
    address_2 = forms.CharField(label="Address line 2")
    city = forms.CharField(label="City")
    province = forms.CharField(label="Province")
    postal_code = forms.CharField(label="Postal code")


class LocationContactForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Location
        fields = ("contact_email", "contact_phone")

    contact_email = forms.EmailField(label="Contact email")
    contact_phone = forms.CharField(label="Contact phone")
