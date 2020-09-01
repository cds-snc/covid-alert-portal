import logging
import requests
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect

from portal.mixins import ThrottledMixin, Is2FAMixin

from .models import COVIDKey


logger = logging.getLogger(__name__)


class CodeView(Is2FAMixin, ThrottledMixin, TemplateView):
    throttled_model = COVIDKey
    throttled_limit = settings.COVID_KEY_MAX_PER_USER
    throttled_time_range = settings.COVID_KEY_MAX_PER_USER_PERIOD_SECONDS
    template_name = "covid_key/key.html"

    def get(self, request):
        return redirect("start")

    @method_decorator(csrf_protect)
    def post(self, request):
        token = request.user.api_key
        diagnosis_code = "0000000000"
        covid_key = None
        if token:
            try:
                try:
                    r = requests.post(
                        settings.API_ENDPOINT,
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    # If we don't get a valid response, throw an exception
                    r.raise_for_status()

                    # Make sure the code has a length of 10, cheap sanity check
                    if len(r.text.strip()) == 10:
                        diagnosis_code = r.text
                    else:
                        logger.error(
                            f"The key API returned a key with the wrong "
                            f"format : {r.text}"
                        )
                        raise Exception(
                            f"The key API returned a key with the wrong "
                            f"format : {r.text}"
                        )
                except requests.exceptions.HTTPError as err:
                    logging.exception(
                        f"Received {r.status_code} with message " f"{err.response.text}"
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
            f"{diagnosis_code[0:3]} {diagnosis_code[3:6]} " f"{diagnosis_code[6:10]}"
        )

        return self.render_to_response(
            {"code": diagnosis_code, "expiry": expiry},
        )

    def limit_reached(self):
        logger.error(
            f"User {self.request.user.email} has hit the limit of {settings.COVID_KEY_MAX_PER_USER} keys per 24h."
        )
        return render(self.request, "covid_key/locked.html", status=403)
