from portal.settings import CREATE_DEFAULT_SU, SU_DEFAULT_PASSWORD
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand
from profiles.models import HealthcareUser

SU_EXISTS = HealthcareUser.objects.filter(name="hcw_portal_admin").exists()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if SU_EXISTS:
            self.stdout.write(self.style.SUCCESS("Default Super User already exists"))
        elif CREATE_DEFAULT_SU and SU_DEFAULT_PASSWORD and not SU_EXISTS:
            self.create_su()
        else:
            self.stdout.write(self.style.SUCCESS("Not creating default Super User"))

    def create_su(self):
        # Check to ensure SU password meets minimum requirements
        # If the password does not meet validation a Validation Error is raised by
        # the validate_password function.
        # https://docs.djangoproject.com/en/3.0/topics/auth/passwords/#django.contrib.auth.password_validation.validate_password
        if validate_password(SU_DEFAULT_PASSWORD) is None:
            HealthcareUser.objects.create_superuser(
                "hcw_portal_admin@cds-snc.ca", "hcw_portal_admin", SU_DEFAULT_PASSWORD
            )
            self.stdout.write(self.style.SUCCESS("Successfully created new super user"))
