from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.db import models
from profiles.models import HealthcareUser
from register.models import Location


SEVERITY = [
    ("1", _("Isolate and get tested")),
    ("2", _("Self-monitor for 14 days")),
    ("3", _("Deprecated Severity")),
]


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    severity = models.CharField(max_length=1, choices=SEVERITY, editable=False)
    start_date = models.DateTimeField(auto_now_add=False, editable=False)
    end_date = models.DateTimeField(auto_now_add=False, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        HealthcareUser, on_delete=models.PROTECT, editable=False
    )
    location = models.ForeignKey(Location, on_delete=models.PROTECT, editable=False)

    @property
    def location_shortcode(self):
        return self.location.short_code

    class Meta:
        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
        ]
        unique_together = [["start_date", "end_date", "location"]]


class NotificationSummary(Notification):
    class Meta:
        proxy = True
        verbose_name = "Notification summary"
        verbose_name_plural = "Notifications summary"
