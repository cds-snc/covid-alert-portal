from uuid import uuid4
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


class HealthcareProvince(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbr = models.SlugField(max_length=3, allow_unicode=True, unique=True)
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
        ontario = HealthcareProvince.objects.get(abbr="ON")
        user = self.create_user(
            email,
            name=name,
            province=ontario,
            password=password,
            is_superuser=True,
            **kwargs,
        )
        user.save(using=self._db)
        return user


class HealthcareUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200, verbose_name=_("Your full name"))
    province = models.ForeignKey(HealthcareProvince, on_delete=models.PROTECT)
    phone_number = PhoneNumberField(
        help_text=_(
            "You must enter a new security code each time you log in. We’ll send the code to your phone number."
        )
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = HealthcareUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone_number"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

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
