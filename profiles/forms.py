from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django import forms
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

from .models import HealthcareUser


class HealthcareAuthenticationForm(AuthenticationForm):
    """
    A login form extending the Django default AuthenticationForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L173
    """

    class Meta:
        model = HealthcareUser

    # override field attributes: https://stackoverflow.com/a/56870308
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(HealthcareAuthenticationForm, self).__init__(*args, **kwargs)

        # remove autofocus from fields
        for field in self.fields:
            self.fields[field].widget.attrs.pop("autofocus", None)

        # update / translate validation message for invalid emails
        self.fields["username"].validators = [
            EmailValidator(message=_("Enter a valid email address"))
        ]


class SignupForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    class Meta:
        model = HealthcareUser
        fields = ("email", "name")


class HealthcareUserEditForm(UserChangeForm):
    password = None
    email = forms.EmailField(widget=forms.EmailInput, disabled=True)

    class Meta:
        model = HealthcareUser
        fields = ("email", "name")
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),
        }
