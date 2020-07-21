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

from phonenumber_field.formfields import PhoneNumberField

from invitations.models import Invitation
from invitations.forms import InviteForm

from .models import HealthcareUser, HealthcareProvince
from .utils import generate_2fa_code


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

    def is_valid(self):
        is_valid = super().is_valid()
        if is_valid is False:
            return is_valid

        user = self.get_user()
        generate_2fa_code(user)

        return is_valid


class Resend2FACodeForm(HealthcareBaseForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if self.user is None or self.user.is_authenticated is False:
            return False

        generate_2fa_code(self.user)
        return True


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
        super().__init__(*args, **kwargs)

        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")


class SignupForm(HealthcareBaseForm, UserCreationForm):
    """A form for creating new users. Extends from UserCreation form, which
    means it includes a repeated password."""

    # disabled fields aren't submitted / ie, can't be modified
    email = forms.CharField(
        widget=forms.TextInput, label=_("Email address"), disabled=True
    )
    province = forms.CharField(widget=forms.HiddenInput, disabled=True)

    name = forms.CharField(label=_("Full name"), validators=[MaxLengthValidator(200)])

    phone_number = PhoneNumberField(
        help_text=_(
            "A single use code will be sent to this phone number everytime you try to login."
        ),
        widget=forms.TextInput(attrs={"placeholder": "+1"}),
    )
    phone_number_confirmation = PhoneNumberField(
        help_text=_("Enter the same phone number as before, for verification"),
        widget=forms.TextInput(attrs={"placeholder": "+1"}),
    )

    field_order = [
        "email",
        "province",
        "name",
        "phone_number",
        "phone_number_confirmation",
        "password1",
        "password2",
    ]

    class Meta:
        model = HealthcareUser
        fields = ("email", "province", "name", "phone_number")

    def clean_province(self):
        # returns a province abbreviation as a string
        # always returns the province abbr from "get_initial"
        province_abbr = self.cleaned_data.get("province", "")
        return HealthcareProvince.objects.get(abbr=province_abbr)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        email_exists = HealthcareUser.objects.filter(email=email)
        if email_exists.count():
            raise ValidationError(_("Email already exists"))
        if not Invitation.objects.filter(email__iexact=email):
            raise ValidationError(_("An invitation hasn't been sent to this address"))

        return email

    def clean_phone_number2(self):
        phone_number = self.cleaned_data.get("phone_number")
        phone_number_confirmation = self.cleaned_data.get("phone_number_confirmation")
        if (
            phone_number
            and phone_number_confirmation
            and phone_number != phone_number_confirmation
        ):
            raise forms.ValidationError(
                _("The phone number fields doesn't match."), code="invalid",
            )
        return phone_number_confirmation


class HealthcareUserEditForm(UserChangeForm):
    password = None
    email = forms.EmailField(widget=forms.EmailInput, disabled=True)
    phone_number = PhoneNumberField()

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

    def validate_invitation(self, email):
        # Delete all non-accepted, valid invitations for the same email, if they exists
        Invitation.objects.all_valid().filter(
            email__iexact=email, accepted=False
        ).delete()
        return super().validate_invitation(email)

    # https://github.com/bee-keeper/django-invitations/blob/9069002f1a0572ae37ffec21ea72f66345a8276f/invitations/forms.py#L60
    def save(self, *args, **kwargs):
        # user is passed by the view
        user = kwargs["user"]
        cleaned_data = super().clean()
        params = {"email": cleaned_data.get("email"), "inviter": user}
        return Invitation.create(**params)
