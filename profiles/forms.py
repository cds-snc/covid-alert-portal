from django.contrib.auth.forms import (
    UserChangeForm,
    AuthenticationForm,
    PasswordResetForm,
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


# TODO: Potentially refactor to extend UserCreationForm
class SignupForm(HealthcareBaseForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    email = forms.EmailField(label=_("Email address"), disabled=True)
    name = forms.CharField(label=_("Full name"), validators=[MaxLengthValidator(200)])
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        help_text=_("At least 12 characters"),
    )
    password2 = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput)

    def clean(self):
        self.cleaned_data = super().clean()
        email = self.cleaned_data.get("email", "").lower()
        email_exists = HealthcareUser.objects.filter(email=email)
        if email_exists.count():
            raise ValidationError(_("Email already exists"))
        if not Invitation.objects.filter(email__iexact=email):
            raise ValidationError(_("An invitation hasn't been sent to this address"))

        self.cleaned_data["email"] = email
        return self.cleaned_data

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) > 200:
            raise ValidationError(_("Name is too long"))
        return name

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match"))

        return password2

    def save(self, commit=True):
        user = HealthcareUser.objects.create_user(
            self.cleaned_data["email"],
            self.cleaned_data["name"],
            self.cleaned_data["password1"],
        )
        return user


class HealthcareUserEditForm(UserChangeForm):
    password = None
    email = forms.EmailField(widget=forms.EmailInput, disabled=True)

    class Meta:
        model = HealthcareUser
        fields = ("email", "name")
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),
        }
