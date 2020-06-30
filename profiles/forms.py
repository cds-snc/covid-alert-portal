from django.contrib.auth.forms import (
    UserChangeForm,
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _

from invitations.models import Invitation
from .models import HealthcareUser


class HealthcareBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(HealthcareBaseForm, self).__init__(*args, **kwargs)


class HealthcareAuthenticationForm(HealthcareBaseForm, AuthenticationForm):
    """
    A login form extending the Django default AuthenticationForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L173
    """

    class Meta:
        model = HealthcareUser

    # override field attributes: https://stackoverflow.com/a/56870308
    def __init__(self, *args, **kwargs):
        super(HealthcareAuthenticationForm, self).__init__(*args, **kwargs)

        # remove autofocus from fields
        for field in self.fields:
            self.fields[field].widget.attrs.pop("autofocus", None)

        # update / translate validation message for invalid emails
        self.fields["username"].validators = [
            EmailValidator(message=_("Enter a valid email address"))
        ]


class HealthcarePasswordResetForm(HealthcareBaseForm, PasswordResetForm):
    """
    A login form extending the Django default PasswordResetForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L251
    """

    def __init__(self, *args, **kwargs):
        super(HealthcarePasswordResetForm, self).__init__(*args, **kwargs)

        # remove autofocus from email
        self.fields["email"].widget.attrs.pop("autofocus", None)
        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")


class SignupForm(HealthcareBaseForm, UserCreationForm):
    """A form for creating new users. Extends from UserCreation form, which
    means it includes a repeated password."""

    name = forms.CharField(label=_("Full name"), validators=[MaxLengthValidator(200)])

    class Meta:
        model = HealthcareUser
        fields = ("email", "name")
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        email_exists = HealthcareUser.objects.filter(email=email)
        if email_exists.count():
            raise ValidationError(_("Email already exists"))
        if not Invitation.objects.filter(email__iexact=email):
            raise ValidationError(_("An invitation hasn't been sent to this address"))

        return email


class HealthcareUserEditForm(UserChangeForm):
    password = None
    email = forms.EmailField(widget=forms.EmailInput, disabled=True)

    class Meta:
        model = HealthcareUser
        fields = ("email", "name")
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),
        }
