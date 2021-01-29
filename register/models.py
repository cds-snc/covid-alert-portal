from uuid import uuid4
from django.db import models
from django.utils.translation import gettext as _


class Registrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200, verbose_name=_("Full name"))

    def __str__(self):  # new
        return "{} ({})".format(self.name, self.email)
