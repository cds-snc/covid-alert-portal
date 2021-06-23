from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from profiles.models import HealthcareUser
from .utils import generate_random_key
from django.utils import timezone


class Registrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    created = models.DateTimeField(default=timezone.now)
    language_cd = models.CharField(max_length=2, default="en")

    def __str__(self):  # new
        return "{}".format(self.email)


class EmailConfirmation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(verbose_name="email", max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    short_code = models.CharField(
        max_length=8, unique=True, null=True, verbose_name=_("Short code")
    )
    category = models.CharField(max_length=200, verbose_name=_("Location category"))
    category_description = models.CharField(
        max_length=200, null=True, verbose_name=_("Location category description")
    )
    name = models.CharField(max_length=200, verbose_name=_("Location name"))
    address = models.CharField(max_length=200, verbose_name=_("Address line 1"))
    address_2 = models.CharField(max_length=200, verbose_name=_("Address line 2"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    province = models.CharField(max_length=100, verbose_name=_("Province"))
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal code"))
    contact_name = models.CharField(
        max_length=200, null=True, verbose_name=_("Name of contact")
    )
    contact_email = models.EmailField(verbose_name=_("Email address"), max_length=255)
    contact_phone = PhoneNumberField(blank=True)
    contact_phone_ext = PhoneNumberField(blank=True, max_length=20)
    created = models.DateTimeField(default=timezone.now)
    registrant = models.ForeignKey(Registrant, on_delete=models.SET_NULL, null=True)

    @property
    def registrant_email(self):
        return self.registrant.email or ''

    # Override save method to generate a unique short code for poster
    def save(self, *args, **kwargs):
        if not self.short_code:
            while True:
                short_code = generate_random_key()
                if not Location.objects.filter(short_code=short_code).exists():
                    break
            self.short_code = short_code
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}, {}, {}, {}".format(
            self.name, self.address, self.city, self.province, self.postal_code
        )


class LocationSummary(Location):
    class Meta:
        proxy = True
        verbose_name = "Location summary"
        verbose_name_plural = "Locations summary"


class Survey(models.Model):
    url = models.URLField(verbose_name=_("General Survey URL"))
    title = models.CharField(max_length=200, verbose_name=_("Survey Title"))
    en_notify_template_id = models.CharField(
        max_length=200, verbose_name=_("English Notify Template ID")
    )
    fr_notify_template_id = models.CharField(
        max_length=200, verbose_name=_("French Notify Template ID")
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class RegistrantSurvey(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.SET_NULL, null=True)
    registrant = models.ForeignKey(Registrant, on_delete=models.SET_NULL, null=True)
    sent_ts = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Sent Timestamp")
    )
    sent_by = models.ForeignKey(HealthcareUser, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registrant}:{self.survey}"
