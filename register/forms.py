from django import forms

from portal.forms import HealthcareBaseForm

from .models import Registrant


class RegistrantCreateForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Registrant

        fields = ("email",)


class RegistrantNameForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Registrant

        fields = ("name",)
