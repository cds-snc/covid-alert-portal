import os
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from profiles.models import HealthcareUser

CREATE_SU = os.getenv("DJANGO_DEFAULT_SU", False) == "True"
SU_PASSWORD = os.getenv("DJANGO_DEFAULT_SU_PASSWORD")
SU_EXISTS = HealthcareUser.objects.filter(name="hcw_portal_admin").exists()

class Command(BaseCommand):

    def handle(self, *args, **options):
        if CREATE_SU and not SU_PASSWORD == "" and not SU_EXISTS:
            HealthcareUser.objects.create_superuser("hcw_portal_admin@cds-snc.ca","hcw_portal_admin", SU_PASSWORD)
            self.stdout.write(self.style.SUCCESS('Successfully created new super user'))
        elif HealthcareUser.objects.filter(name="hcw_portal_admin").exists():
            self.stdout.write(self.style.SUCCESS('Default Super User already exists'))
        else:
          self.stdout.write(self.style.SUCCESS('Not creating default Super User'))