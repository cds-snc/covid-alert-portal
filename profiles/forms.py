from django.contrib.auth.forms import (
    UserChangeForm,
    AuthenticationForm,
)
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

from invitations.models import Invitation
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


class SignupForm(forms.Form):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')  
        super(SignupForm, self).__init__(*args, **kwargs)
    
    email = forms.EmailField(label=_("Email Address"), disabled = True)
    name = forms.CharField(label=_("Full name"))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, help_text="At least 12 characters")
    password2 = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput)


    def clean(self):
        self.cleaned_data = super().clean()
        email = self.cleaned_data.get('email', '').lower()
        email_exists = HealthcareUser.objects.filter(email=email)
        if email_exists.count():
            raise  ValidationError(_("Email already exists"))
        if not Invitation.objects.filter(email__iexact=email):
            raise  ValidationError(_("An invitation hasn't been sent to this address"))

        self.cleaned_data['email'] = email
        return self.cleaned_data
 
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name)>200:
            raise  ValidationError(_("Name is too long"))
        return name
   
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Password don't match"))

        #We probably don't actually need this here and can rely on AUTH_PASSWORD_VALIDATORS
        if len(password2) < 12:
            raise ValidationError(_("Password must be at least 12 characters"))

        return password2
 
    def save(self, commit=True):
        user = HealthcareUser.objects.create_user(
            self.cleaned_data['email'],
            self.cleaned_data['name'],
            self.cleaned_data['password1']
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
