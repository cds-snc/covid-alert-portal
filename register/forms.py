from django import forms

from portal.forms import HealthcareBaseForm

from .models import Registrant


class EmailForm(HealthcareBaseForm, forms.Form):
    email = forms.EmailField(label="Email address")


class RegistrantNameForm(HealthcareBaseForm, forms.ModelForm):
    class Meta:
        model = Registrant

        fields = ("name",)
