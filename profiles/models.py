from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class HealthcareProvince(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbr = models.SlugField(max_length=2, allow_unicode=True, unique=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.abbr)

    class Meta:
        ordering = ["abbr"]
        verbose_name_plural = "provinces"


class HealthcareUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email and password
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), name=name, province="ON")

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
    province = models.ForeignKey(HealthcareProvince, on_delete=models.PROTECT)

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
