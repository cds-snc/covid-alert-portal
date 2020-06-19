from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import HealthcareUser


class SignupForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    class Meta:
        model = HealthcareUser
        fields = ('email', 'name', 'language')


class HealthcareUserEditForm(UserChangeForm):
    password = None
    email = forms.EmailField(widget=forms.EmailInput, disabled=True)

    class Meta:
        model = HealthcareUser
        fields = ('email', 'name', 'language')
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }
