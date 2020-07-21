from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _
from .models import HealthcareUser


def generate_2fa_code(user: HealthcareUser):
    sms_devices = user.notifysmsdevice_set.all()
    for sms_device in sms_devices:
        sms_device.generate_challenge()


def get_site_name(request=None):
    current_site = get_current_site(request) if request else Site.objects.get_current()

    # if example.com is our domain, we're either on localhost or a Heroku PR app
    if current_site.domain == "example.com":
        environment = (
            "[{}]".format(settings.HEROKU_APP_NAME)
            if settings.HEROKU_APP_NAME
            else "[Localhost]"
        )

        return "{} {}".format(environment, _("COVID Alert Portal"))

    return current_site.name
