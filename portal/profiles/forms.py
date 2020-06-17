from django.contrib.auth.forms import UserCreationForm

from .models import HealthcareUser


class SignupForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    class Meta:
        model = HealthcareUser
        fields = ('email', 'name', 'language')
