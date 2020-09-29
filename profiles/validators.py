from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    UserAttributeSimilarityValidator,
    NumericPasswordValidator,
)
from django.utils.translation import ugettext as _

from .utils._banned_passwords import banned_passwords, banned_partial_passwords


class BannedPasswordValidator(object):
    def validate(self, password, user=None):
        if password in banned_passwords:
            raise ValidationError(
                _("Your password must be more difficult to guess."),
                code="password_banned",
            )

        for partial in banned_partial_passwords:
            if partial.lower() in password.lower():
                raise ValidationError(
                    _("Your password cannot include anything about COVID."),
                    code="password_banned_partial",
                )

    def get_help_text(self):
        return _("Your password must be hard to guess.")


class HealthcareMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Your password needs at least %(min_length)d characters.")
                % {"min_length": self.min_length},
                code="password_too_short",
            )

    def get_help_text(self):
        return _("Your password must be at least %(min_length)d characters.") % {
            "min_length": self.min_length
        }


class HealthcareUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            return super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _(
                    "Your password must be different from your other personal information."
                ),
                code="password_too_similar",
            )

    def get_help_text(self):
        return _("Your password cannot be similar to your name or email address.")


class HealthcareNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _(
                    "Your password cannot be only numbers. It must have letters or other characters also."
                ),
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return _("Your password cannot be only numbers.")
