from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings
import datetime

LEVEL_CHOICES = (
    ("warning", "Warning"),
    ("error", "Error"),
    ("success", "Success"),
    ("info", "Info"),
)


class Announcement(models.Model):
    """
    Model to hold global announcements
    """

    title_en = models.CharField(_("Title in English"), max_length=100, blank=False)
    title_fr = models.CharField(_("Title in French"), max_length=100, blank=False)
    content_en = models.TextField(_("English Content"), blank=True)
    content_fr = models.TextField(_("French Content"), blank=True)
    display = models.BooleanField(_("show_to_users"), default=False)
    level = models.CharField(max_length=7, choices=LEVEL_CHOICES, default="info")
    creation_date = models.DateTimeField(_("creation_date"), auto_now=True)
    site_wide = models.BooleanField(_("site wide"), default=False)
    for_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("for_user"),
        on_delete=models.CASCADE,
    )
    dismissable = models.BooleanField(_("dismissable"), default=False)
    publish_start = models.DateField(_("publish_start"), default=datetime.date.today)
    publish_end = models.DateField(_("publish_end"), blank=True, null=True)

    def dismiss_url(self):
        if self.dismissable:
            return reverse("announcements:dismiss", args=[self.pk])
