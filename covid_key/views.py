import logging
import requests
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django_otp.decorators import otp_required


logger = logging.getLogger(__name__)


@login_required
@otp_required
def code(request):
    token = settings.API_AUTHORIZATION
    diagnosis_code = "0000000000"
    if token:
        try:
            r = requests.post(
                settings.API_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
            )
            r.raise_for_status()  # If we don't get a valid response, throw an exception
            # Make sure the code has a length of 10, cheap sanity check
            if len(r.text.strip()) == 10:
                diagnosis_code = r.text
            else:
                logger.error(
                    f"The key API returned a key with the wrong format : {r.text}"
                )
        except requests.exceptions.HTTPError as err:
            logging.exception(
                f"Received {r.status_code} with message {err.response.text}"
            )
        except requests.exceptions.RequestException as err:
            logging.exception(f"Something went wrong {err}")

    # Split up the code with a space in the middle so it looks like this: 123 456 789
    diagnosis_code = (
        f"{diagnosis_code[0:3]} {diagnosis_code[3:6]} {diagnosis_code[6:10]}"
    )

    expiry = timezone.now() + timedelta(days=1)

    template_name = "key_instructions" if "/key-instructions" in request.path else "key"

    return render(
        request,
        "profiles/{}.html".format(template_name),
        {"code": diagnosis_code, "expiry": expiry},
    )
