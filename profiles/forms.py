from django.contrib.auth.forms import (
    UserChangeForm,
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django import forms
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import EmailValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django_otp.plugins.otp_email.conf import settings as otp_settings

from invitations.models import Invitation
from .models import HealthcareUser, HealthcareProvince


class HealthcareBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Remove the colon after field labels
        kwargs.setdefault("label_suffix", "")
        super(HealthcareBaseForm, self).__init__(*args, **kwargs)

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

    def is_valid(self):
        is_valid = super().is_valid()
        if is_valid is False:
            return is_valid

        user = self.get_user()
        email_devices = user.emaildevice_set.all()
        # If the user has no email device, create one with his email
        if len(email_devices) == 0:
            email_device = user.emaildevice_set.create()
        else:
            email_device = email_devices[0]

        # I cant use the email_device.generate_challenge() directly here, I need to pass more context into the emails
        email_device.generate_token(valid_secs=otp_settings.OTP_EMAIL_TOKEN_VALIDITY)

        context = {
            "token": email_device.token,
            "full_name": user.name,
            "service_name": settings.SERVICE_NAME,
        }
        body = get_template("otp/email/token.html").render(context)

        send_mail(
            otp_settings.OTP_EMAIL_SUBJECT,
            body,
            otp_settings.OTP_EMAIL_SENDER,
            [user.email],
        )

        return is_valid


class Healthcare2FAForm(HealthcareBaseForm):
    code = forms.CharField(
        widget=forms.TextInput,
        label=_("Please enter the security code."),
        required=True,
    )


class HealthcarePasswordResetForm(HealthcareBaseForm, PasswordResetForm):
    """
    A login form extending the Django default PasswordResetForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L251
    """

    def __init__(self, *args, **kwargs):
        super(HealthcarePasswordResetForm, self).__init__(*args, **kwargs)

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
