from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.contrib.auth import password_validation
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField

from invitations.models import Invitation
from invitations.forms import (
    InviteForm,
    InvitationAdminAddForm,
    InvitationAdminChangeForm,
)

from portal.forms import HealthcareBaseForm
from .models import HealthcareUser, HealthcareProvince
from .utils import generate_2fa_code


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
        self.fields["username"].label = _("Email address")

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


class HealthcareBaseEditForm(HealthcareBaseForm, forms.ModelForm):
    template_name = "profiles/edit.html"

    class Meta:
        abstract = True


class HealthcareEmailEditForm(HealthcareBaseEditForm):
    title = _("Change your email")

    class Meta:
        model = HealthcareUser
        fields = ("email",)


class HealthcareNameEditForm(HealthcareBaseEditForm):
    title = _("Change your name")

    class Meta:
        model = HealthcareUser
        fields = ("name",)


class HealthcarePhoneEditForm(HealthcareBaseEditForm):
    title = _("Change your phone number")
    phone_number2 = PhoneNumberField(
        label=_("Confirm your phone number"),
        help_text=_("Enter the same phone number as above."),
    )

    class Meta:
        model = HealthcareUser
        fields = ("phone_number",)

    def clean_phone_number2(self):
        phone_number = self.cleaned_data.get("phone_number")
        phone_number2 = self.cleaned_data.get("phone_number2")
        if phone_number and phone_number2 and phone_number != phone_number2:
            raise ValidationError(
                _("Phone numbers provided does not match."),
                code="phone_number_mismatch",
            )
        return phone_number2


class HealthcarePasswordEditForm(HealthcareBaseEditForm):
    title = _("Change your password")
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = HealthcareUser
        fields = ()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"], code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


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
            "A single use code will be sent to this phone number every time you try to log in."
        ),
    )
    phone_number_confirmation = PhoneNumberField(
        help_text=_("Enter the same phone number as before, for verification"),
    )

    field_order = [
        "name",
        "email",
        "province",
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

    def clean_phone_number_confirmation(self):
        phone_number = self.cleaned_data.get("phone_number")
        phone_number_confirmation = self.cleaned_data.get("phone_number_confirmation")
        if (
            phone_number
            and phone_number_confirmation
            and phone_number != phone_number_confirmation
        ):
            raise forms.ValidationError(
                _("The phone number fields don‘t match."), code="invalid",
            )
        return phone_number_confirmation


class HealthcareInviteForm(HealthcareBaseForm, InviteForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")

    def validate_invitation(self, email):
        # Delete all non-accepted invitations for the same email, if they exist
        Invitation.objects.filter(email__iexact=email, accepted=False).delete()
        return super().validate_invitation(email)

    # https://github.com/bee-keeper/django-invitations/blob/9069002f1a0572ae37ffec21ea72f66345a8276f/invitations/forms.py#L60
    def save(self, *args, **kwargs):
        # user is passed by the view
        user = kwargs["user"]
        cleaned_data = super().clean()
        params = {"email": cleaned_data.get("email"), "inviter": user}
        return Invitation.create(**params)


class HealthcareInvitationAdminAddForm(InvitationAdminAddForm):
    def save(self, *args, **kwargs):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        params = {
            "email": email,
            "inviter": self.request.user,
        }
        instance = Invitation.create(**params)
        instance.send_invitation(self.request)
        # We can't call InvitationAdminForm here, it would try to send 2 invitations
        super(forms.ModelForm, self).save(*args, **kwargs)
        return instance

    class Meta:
        fields = ("email",)


class HealthcareInvitationAdminChangeForm(InvitationAdminChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["inviter"].disabled = True
