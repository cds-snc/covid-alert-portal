from django import forms

from portal.forms import HealthcareBaseForm
from django.utils.translation import gettext_lazy as _
from .models import Registrant
from portal.widgets import CDSRadioWidget


class EmailForm(HealthcareBaseForm, forms.Form):
    email = forms.EmailField(label="Email address")


class RegistrantNameForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Registrant

        fields = ("name",)

class LocationCategoryForm(HealthcareBaseForm, forms.Form):
    category = forms.ChoiceField(
        label="",
        choices=[
            ("accommodation", _("Yes, generate a key for another patient.")),
            ("childcare", _("No, try again or use different phone number.")),
            ("education", _("Education")),
            ("medical", _("Medical Facility")),
            ("restaurant", _("Restaurant, cafe, pub or bar")),
            ("retail", _("Retail store")),
            ("transport", _("Transport")),
            ("other", _("Other")),
        ],
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )

class LocationNameForm(HealthcareBaseForm, forms.Form):
    name = forms.CharField(label="What is the name of your business, organization or event?")