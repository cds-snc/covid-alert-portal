from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from .utils._banned_passwords import banned_passwords, banned_partial_passwords


class BannedPasswordValidator(object):
    def validate(self, password, user=None):
        if password in banned_passwords:
            raise ValidationError(
                _("Your password can’t be a commonly-used sequence"),
                code="password_banned",
            )

        for partial in banned_partial_passwords:
            if partial.lower() in password.lower():
                raise ValidationError(
                    _("Your password can’t contain terms related to COVID-19"),
                    code="password_banned_partial",
                )

    def get_help_text(self):
        return _("Your password can’t be a commonly-used sequence.")
