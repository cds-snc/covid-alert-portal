from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language

from phonenumber_field.formfields import PhoneNumberField

from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient

from otp_yubikey.models import RemoteYubikeyDevice, ValidationService

from invitations.models import Invitation
from invitations.forms import (
    InviteForm,
    InvitationAdminAddForm,
    InvitationAdminChangeForm,
)

from portal.forms import HealthcareBaseForm
from .models import HealthcareUser, HealthcareProvince, AuthorizedDomain
from .utils import generate_2fa_code


validation_messages = {
    "code": {
        "required": _("Enter information to continue"),
    },
    "email": {
        "required": _("Enter your email address"),
    },
    "name": {
        "required": _("Enter your name"),
    },
    "password": {"required": _("Enter your password")},
    "password2": {"required": _("Enter the same password again")},
    "phone_number": {"required": _("Enter your phone number")},
    "phone_number2": {"required": _("Enter the same phone number again")},
    "username": {
        "required": _("Enter your email address for the COVID Alert Portal"),
    },
}


class HealthcareAuthenticationForm(HealthcareBaseForm, AuthenticationForm):
    """
    A login form extending the Django default AuthenticationForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L173
    """

    error_messages = {
        "invalid_login": _(
            "Your username or password do not match our records.  Check if “caps lock” is on or off."
        ),
        "inactive": _("This account is inactive."),
    }

    class Meta:
        model = HealthcareUser

    def __init__(self, *args, **kwargs):
        super(HealthcareAuthenticationForm, self).__init__(*args, **kwargs)

        # update / translate validation message for invalid emails
        self.fields["username"].validators = [
            EmailValidator(message=_("Enter a valid email address"))
        ]
        self.fields["username"].label = _("Email address")
        self.fields["username"].error_messages["required"] = validation_messages[
            "username"
        ]["required"]
        self.fields["password"].error_messages["required"] = validation_messages[
            "password"
        ]["required"]

    # lowercase all email addresses entered into the login form
    def clean_username(self):
        return self.cleaned_data["username"].lower()

    def is_valid(self):
        is_valid = super().is_valid()
        if is_valid is False:
            return is_valid

        user = self.get_user()

        if user.remoteyubikeydevice_set.first() is None:
            # Dont send SMS if the user has a Yubikey
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
        label=_("Security code"),
        required=True,
    )
    code.error_messages["required"] = validation_messages["code"]["required"]


class HealthcareBaseEditForm(HealthcareBaseForm, forms.ModelForm):
    template_name = "profiles/edit.html"

    class Meta:
        abstract = True


class HealthcareNameEditForm(HealthcareBaseEditForm):
    title = _("Change your name")
    name = forms.CharField(
        label=_("Full name"),
    )
    name.error_messages["required"] = validation_messages["name"]["required"]

    class Meta:
        model = HealthcareUser
        fields = ("name",)


class HealthcarePhoneEditForm(HealthcareBaseEditForm):
    title = _("Change your mobile phone number")
    phone_number = PhoneNumberField(
        label=_("Mobile phone number"),
        help_text=_(
            "You must enter a new security code each time you log in. We’ll text the code to your mobile phone number."
        ),
    )
    phone_number.error_messages["required"] = validation_messages["phone_number"][
        "required"
    ]

    phone_number2 = PhoneNumberField(
        label=_("Confirm your mobile phone number"),
        help_text=_("Enter the same mobile number as above."),
    )
    phone_number2.error_messages["required"] = validation_messages["phone_number2"][
        "required"
    ]

    error_messages = {
        "phone_number_mismatch": _("You entered 2 different phone numbers."),
    }

    class Meta:
        model = HealthcareUser
        fields = ("phone_number",)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        phone_number2 = self.data.get("phone_number2")
        if phone_number and phone_number2 and phone_number != phone_number2:
            raise ValidationError(
                self.error_messages.get("phone_number_mismatch"),
                code="phone_number_mismatch",
            )
        return phone_number


class HealthcarePasswordEditForm(HealthcareBaseEditForm):
    title = _("Change your password")
    error_messages = {
        "password_mismatch": _("You entered 2 different passwords."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password1.error_messages["required"] = validation_messages["password"]["required"]

    password2 = forms.CharField(
        label=_("Confirm your password"),
        widget=forms.PasswordInput(),
        strip=False,
        help_text=_("Enter the same password as above."),
    )
    password2.error_messages["required"] = validation_messages["password2"]["required"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = HealthcareUser
        fields = ()

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        # We can't use clean_data for password2, it hasn't been cleaned yet
        password2 = self.data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password1

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password1")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password1", error)

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()

        return self.user


class HealthcarePasswordResetForm(HealthcareBaseForm, PasswordResetForm):
    """
    A login form extending the Django default PasswordResetForm.
    https://github.com/django/django/blob/9a54a9172a724d38caf6a150f41f23d79b9bdbb7/django/contrib/auth/forms.py#L251
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")
        self.fields["email"].error_messages["required"] = validation_messages["email"][
            "required"
        ]

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        user = context.get("user")
        url = context.get("base_url") + reverse(
            "password_reset_confirm",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": context.get("token"),
            },
        )
        notifications_client = NotificationsAPIClient(
            settings.NOTIFY_API_KEY, base_url=settings.NOTIFY_ENDPOINT
        )

        try:
            notifications_client.send_email_notification(
                email_address=user.email,
                template_id=settings.PASSWORD_RESET_EMAIL_TEMPLATE_ID.get(
                    context.get("language") or "en"
                ),
                personalisation={
                    "name": user.name,
                    "url": url,
                },
            )
        except HTTPError as e:
            raise Exception(e)


class HealthcarePasswordResetConfirm(HealthcareBaseForm, SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password1.error_messages["required"] = validation_messages["password"][
        "required"
    ]

    new_password2 = forms.CharField(
        label=_("Confirm your new password"),
        strip=False,
        widget=forms.PasswordInput(),
        help_text=_("Enter the same password as above."),
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")
        # We can't use clean_data for password2, it hasn't been cleaned yet
        password2 = self.data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        password_validation.validate_password(password1, self.user)
        return password1

    def clean_new_password2(self):
        pass


class SignupForm(HealthcareBaseForm, UserCreationForm, forms.ModelForm):
    """A form for creating new users. Extends from UserCreation form, which
    means it includes a repeated password."""

    # disabled fields aren't submitted / ie, can't be modified
    email = forms.CharField(
        widget=forms.TextInput, label=_("Email address"), disabled=True
    )
    province = forms.CharField(widget=forms.HiddenInput, disabled=True)

    name = forms.CharField(label=_("Full name"), validators=[MaxLengthValidator(200)])
    name.error_messages["required"] = validation_messages["name"]["required"]

    phone_number = PhoneNumberField(
        label=_("Mobile phone number"),
        help_text=_(
            "You must enter a new security code each time you log in. We’ll text the code to your mobile phone number."
        ),
    )
    phone_number.error_messages["required"] = validation_messages["phone_number"][
        "required"
    ]

    phone_number_confirmation = PhoneNumberField(
        label=_("Confirm your phone number"),
        help_text=_("Enter the same mobile number as above."),
    )

    password1 = forms.CharField(widget=forms.PasswordInput())
    password1.error_messages["required"] = validation_messages["password"]["required"]

    password2 = forms.CharField(
        label=_("Confirm your password"),
        help_text=_("Enter the same password as above."),
        strip=False,
        widget=forms.PasswordInput(),
    )
    password2.error_messages["required"] = validation_messages["password2"]["required"]

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

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        # We can't use clean_data for password2, it hasn't been cleaned yet
        password2 = self.data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password1

    def clean_password2(self):
        # We actually dont want this function to run in UserCreationForm
        # The logic has been moved to clean_password
        pass

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        email_exists = HealthcareUser.objects.filter(email=email)
        if email_exists.count():
            raise ValidationError(_("Email already exists"))
        if not Invitation.objects.filter(email__iexact=email):
            raise ValidationError(_("An invitation hasn’t been sent to this address"))

        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        # We can't use clean_data for phone_number_confirmation, it hasn't been cleaned yet
        phone_number_confirmation = self.data.get("phone_number_confirmation")
        if (
            phone_number
            and phone_number_confirmation
            and phone_number != phone_number_confirmation
        ):
            raise forms.ValidationError(
                _("The phone numbers didn’t match."),
                code="invalid",
            )
        return phone_number

    def _post_clean(self):
        # This function is the same as UserCreationForm._post_clean, except we
        # are pinning the error on field password1 instead of password2 for
        # accessibility reasons
        forms.ModelForm._post_clean(self)
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password1")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password1", error)


class HealthcareInviteForm(HealthcareBaseForm, InviteForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Otherwise it just says "Email"
        self.fields["email"].label = _("Email address")

    def validate_invitation(self, email):
        account_exists = HealthcareUser.objects.filter(email=email).count()
        if not account_exists:
            # If there is no user account, delete any prior invitations to this email
            Invitation.objects.filter(email__iexact=email).delete()

        return super().validate_invitation(email)

    def clean_email(self):
        try:
            email = super().clean_email()
        except ValidationError:
            # it is no longer possible to get the "already invited" or the "already accepted" error messages
            # without having an existing Portal account
            raise forms.ValidationError(
                _("This email address already has a portal account.")
            )

        try:
            # If the email is invalid, an error would have been raised by
            # the CleanEmailMixin
            domain = email[email.find("@") + 1 :]
            AuthorizedDomain.objects.get(domain=domain)
        except AuthorizedDomain.DoesNotExist:
            if settings.DEBUG is False or settings.TESTING is True:
                if AuthorizedDomain.objects.filter(domain="*").count() == 0:
                    raise forms.ValidationError(
                        _(
                            "You cannot invite ‘%(email)s’ to create an account because ‘@%(domain)s’ is not on the portal’s safelist."
                        )
                        % {"domain": domain, "email": email}
                    )
        return email

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
        instance.send_invitation(self.request, language=get_language())
        # We can't call InvitationAdminForm here, it would try to send 2 invitations
        super(forms.ModelForm, self).save(*args, **kwargs)
        return instance

    class Meta:
        fields = ("email",)


class HealthcareInvitationAdminChangeForm(InvitationAdminChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["inviter"].disabled = True


# heavily inspired by https://github.com/ossobv/kleides-mfa/blob/ec93f141761b188dd2a2ecf8bbb525a9da47270e/kleides_mfa/forms.py#L187
class YubikeyDeviceCreateForm(HealthcareBaseForm, forms.ModelForm):
    otp_token = forms.CharField(label=_("Token"))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["otp_token"].widget.attrs.update({"autofocus": "autofocus"})
        self.instance.user = user

    def clean(self):
        cleaned_data = super().clean()
        token = self.cleaned_data.get("otp_token")
        service = ValidationService.objects.first()
        verified = False
        # names can have a maximum length of 32 characters
        cleaned_data["name"] = self.instance.user.email[:32]

        if token and service:
            self.instance.service = service
            self.instance.public_id = token[:-32]
            verified = self.instance.verify_token(token)
        if not verified:
            raise forms.ValidationError(
                _("Unable to validate the token with the device.")
            )
        return cleaned_data

    class Meta:
        model = RemoteYubikeyDevice
        fields = ("otp_token",)


# heavily inspired by: https://github.com/ossobv/kleides-mfa/blob/ec93f141761b188dd2a2ecf8bbb525a9da47270e/kleides_mfa/forms.py#L39
class YubikeyVerifyForm(HealthcareBaseForm, forms.Form):
    otp_token = forms.CharField(label=_("Token"))

    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop("device", None)
        super().__init__(*args, **kwargs)
        self.fields["otp_token"].widget.attrs.update({"autofocus": "autofocus"})

    def get_device(self):
        if self.is_valid():
            return self.device
        return None

    def clean(self):
        cleaned_data = super().clean()
        token = cleaned_data.get("otp_token")
        if not token:  # token is a required field.
            return cleaned_data

        # Note that tokens can become invalid once verified
        if not self.device.verify_token(token):
            raise forms.ValidationError(_("The token is not valid for this device."))
        return cleaned_data
