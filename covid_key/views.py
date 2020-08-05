import logging
import requests
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django_otp.decorators import otp_required
from django.utils.translation import gettext as _

from .models import COVIDKey


logger = logging.getLogger(__name__)


@login_required
@otp_required
def code(request):
    created_keys_count = COVIDKey.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    if created_keys_count < settings.COVID_KEY_MAX_PER_USER_PER_DAY:
        return _generate_key(request)
    else:
        logger.error(
            f"User {request.user.email} has hit the limit of {settings.COVID_KEY_MAX_PER_USER_PER_DAY} keys per 24h."
        )
        return _key_throttled(request)


def _generate_key(request):
    token = settings.API_AUTHORIZATION
    diagnosis_code = "0000000000"
    covid_key = None
    if token:
        try:
            try:
                r = requests.post(
                    settings.API_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
                )
                # If we don't get a valid response, throw an exception
                r.raise_for_status()

                # Make sure the code has a length of 10, cheap sanity check
                if len(r.text.strip()) == 10:
                    diagnosis_code = r.text
                else:
                    logger.error(
                        f"The key API returned a key with the wrong format : {r.text}"
                    )
                    raise Exception(
                        f"The key API returned a key with the wrong format : {r.text}"
                    )
            except requests.exceptions.HTTPError as err:
                logging.exception(
                    f"Received {r.status_code} with message {err.response.text}"
                )
                raise err
            except requests.exceptions.RequestException as err:
                logging.exception(f"Something went wrong {err}")
                raise err
            else:
                covid_key = COVIDKey()
                covid_key.created_by = request.user
                covid_key.expiry = timezone.now() + timedelta(days=1)
                covid_key.save()

        except Exception:
            diagnosis_code = ""
            messages.add_message(
                request,
                messages.ERROR,
                _("Something went wrong. Contact your manager."),
                "covid_key",
            )

    if covid_key is None:
        expiry = timezone.now() + timedelta(days=1)
    else:
        expiry = covid_key.expiry

    # Split up the code with a space in the middle so it looks like this:
    # 123 456 789
    diagnosis_code = (
        f"{diagnosis_code[0:3]} {diagnosis_code[3:6]} {diagnosis_code[6:10]}"
    )

    return render(
        request, "covid_key/key.html", {"code": diagnosis_code, "expiry": expiry},
    )


def _key_throttled(request):
    return render(request, "covid_key/throttled.html",)
