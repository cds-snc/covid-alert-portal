from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from portal import settings

LANGUAGE_CHOICES = (
    ("en", "English"),
    ("fr", "French"),
)

PROVINCE_CHOICES = (
    ("bc", "British Columbia"),
    ("ab", "Alberta"),
    ("sk", "Saskachewan"),
    ("mb", "Manitoba"),
    ("on", "Ontario"),
    ("qc", "Quebec"),
    ("ns", "Nova Scotia"),
    ("nb", "New Brunswick"),
    ("nl", "Newfoundland"),
    ("pe", "Prince Edward Island"),
    ("yk", "Yukon"),
    ("nt", "Northwest Territories"),
    ("nu", "Nunavut"),
)


class HealthcareUserManager(BaseUserManager):
    def create_user(self, email, name, language="en", password=None):
        """
        Creates and saves a User with the given email, language
         and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email), name=name, language=language
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(email, password=password, name=name,)
        user.is_admin = True
        user.save(using=self._db)
        return user


class HealthcareUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True,
    )
    name = models.CharField(max_length=200)
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )
    province = models.CharField(max_length=25, choices=PROVINCE_CHOICES, default="nu")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = HealthcareUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

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
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin
