from django.db import models
from django.utils.translation import gettext as _
from solo.models import SingletonModel


class GoogleAnalytics(SingletonModel):
    """
    Model to hold Google Anaytlics code
    """

    ga_code = models.CharField(
        _("Google Analytics Code"),
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text=_(
            "If no tracking code provided Google Analytics will not record any data for site."
        ),
    )

    def __str__(self):
        return _("Google Analytics V4 Tracking Code")

    class Meta:
        verbose_name = _("Google Analytics V4 Tracking Code")
