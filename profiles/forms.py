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
from invitations.forms import InviteForm

from .models import HealthcareUser, HealthcareProvince


class HealthcareBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Remove the colon after field labels
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

        # override field attributes: https://stackoverflow.com/a/56870308
        for field in self.fields:
            self.fields[field].widget.attrs.pop("autofocus", None)


class HealthcareAuthenticationForm(HealthcareBaseForm, AuthenticationForm):
    """
    A login form extending the Django default AuthenticationForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L173
    """

    class Meta:
        model = HealthcareUser

    def __init__(self, *args, **kwargs):
        super(HealthcareAuthenticationForm, self).__init__(*args, **kwargs)

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
        super().__init__(*args, **kwargs)

        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")


class SignupForm(HealthcareBaseForm, UserCreationForm):
    """A form for creating new users. Extends from UserCreation form, which
    means it includes a repeated password."""

    # disabled fields aren't submitted
    email = forms.CharField(
        widget=forms.TextInput, label=_("Email address"), disabled=True
    )
    province = forms.CharField(
        widget=forms.TextInput, label=_("Province"), disabled=True
    )

    name = forms.CharField(label=_("Full name"), validators=[MaxLengthValidator(200)])

    class Meta:
        model = HealthcareUser
        fields = ("email", "province", "name")

    def clean_province(self):
        # returns a province name as a string
        # always returns the province name from "get_initial"
        province_name = self.cleaned_data.get("province", "")
        return HealthcareProvince.objects.get(name=province_name)

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


class HealthcareInviteForm(HealthcareBaseForm, InviteForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")

    # https://github.com/bee-keeper/django-invitations/blob/9069002f1a0572ae37ffec21ea72f66345a8276f/invitations/forms.py#L60
    def save(self, *args, **kwargs):
        # user is passed by the view
        user = kwargs["user"]
        cleaned_data = super().clean()
        params = {"email": cleaned_data.get("email"), "inviter": user}
        return Invitation.create(**params)
