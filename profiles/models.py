from uuid import uuid4
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


class HealthcareProvince(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbr = models.SlugField(max_length=5, allow_unicode=True, unique=True)
    sms_enabled = models.BooleanField(default=False)
    qr_code_enabled = models.BooleanField(default=False)
    api_key = models.CharField(
        null=True, blank=True, max_length=256, verbose_name=_("Bearer token")
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.abbr)

    class Meta:
        ordering = ["abbr"]
        verbose_name_plural = "provinces"


class HealthcareUserManager(BaseUserManager):
    def create_user(
        self, email, password=None, is_admin=False, is_superuser=False, **kwargs
    ):
        """
        Creates and saves a User with the given email and password
        """
        if not email:
            raise ValueError("Users must have an email address")

        # force is_admin to True when creating a superuser
        if is_superuser:
            is_admin = True

        user = self.model(
            email=self.normalize_email(email),
            is_admin=is_admin,
            is_superuser=is_superuser,
            **kwargs,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password, **kwargs):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        cds = HealthcareProvince.objects.get(abbr="CDS")
        user = self.create_user(
            email,
            name=name,
            province=cds,
            password=password,
            is_superuser=True,
            **kwargs,
        )
        user.save(using=self._db)
        return user


class HealthcareUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200, verbose_name=_("Full name"))
    province = models.ForeignKey(HealthcareProvince, on_delete=models.PROTECT)
    phone_number = PhoneNumberField(
        help_text=_(
            "You must enter a new code each time you log in. We’ll text the log in code to your mobile phone number."
        ),
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(
        null=True,
        help_text=_("If set, the user will be blocked until that time."),
        blank=True,
    )
    # this is only used for sending surveys right now, if used for other purpose
    # this should be captured in the Portal before use to ensure accuracy
    language_cd = models.CharField(max_length=2, default="en")

    objects = HealthcareUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        if perm == "sms_enabled":
            # sms_enabled requires a special check because it's not an actual permission, but a property of the province
            return self.province.sms_enabled
        return super().has_perm(perm, obj)

    class Meta:
        permissions = [("can_send_alerts", "Can send outbreak alerts")]

    @property
    def api_key(self):
        """
        Making a property here just in case we decide to be even ore granular in the future
        (api key per user or HCW group)
        """
        api_key = self.province.api_key
        if api_key is None or api_key == "":
            api_key = settings.API_AUTHORIZATION
        return api_key

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Only superusers can use the django backend
        return self.is_superuser

    @property
    def can_send_alerts(self):
        return self.has_perm("profiles.can_send_alerts")


class HealthcareFailedAccessAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    time = models.DateTimeField(_("Attempt Time"), auto_now_add=True, editable=False)
    username = models.CharField(max_length=256, null=False)


class AuthorizedDomain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    domain = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.domain
