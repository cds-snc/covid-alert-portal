import logging
import requests
from datetime import timedelta, datetime
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from portal.mixins import ThrottledMixin, Is2FAMixin

from .forms import OtkSmsForm, OtkSmsSentForm
from .models import COVIDKey


logger = logging.getLogger(__name__)


class PortalLandingView(TemplateView):
    template_name = "covid_key/landing.html"

    def get(self, request):
        if not request.user.can_send_alerts:
            return HttpResponseRedirect(reverse_lazy("start"))
        return super().get(request)


class OTKStartView(TemplateView):
    template_name = "covid_key/start.html"

    def get(self, request):
        # clear any existing one time keys
        self.request.session.pop("otk", None)
        return super().get(request)


class SessionTemplateView(TemplateView):
    def get(self, request, **kwargs):
        if "otk" in self.request.session:
            # if we have a cached OTK, let's display it
            return super().get(request, kwargs)
        else:
            # if we don't have a cached OTK then redirect back to the start
            return redirect("landing")


class CodeView(Is2FAMixin, ThrottledMixin, SessionTemplateView):
    throttled_model = COVIDKey
    throttled_limit = settings.COVID_KEY_MAX_PER_USER
    throttled_time_range = settings.COVID_KEY_MAX_PER_USER_PERIOD_SECONDS
    template_name = "covid_key/key.html"

    def get_context_data(self, **kwargs):
        # Load cached OTK when displaying from a GET request
        context = super().get_context_data(**kwargs)
        context["sms_enabled"] = self.request.user.province.sms_enabled
        context["code"] = self.request.session.get("otk")["code"]
        context["expiry"] = datetime.fromtimestamp(
            self.request.session.get("otk")["expiry"]
        )
        return context

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
                    covid_key = COVIDKey.objects.create(
                        created_by=request.user,
                        created_by_email=request.user.email,
                        expiry=timezone.now() + timedelta(days=1),
                    )

            except Exception:
                diagnosis_code = ""
                messages.add_message(
                    request,
                    messages.ERROR,
                    _("Something went wrong. Contact your administrator."),
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

        # Cache the key temporarily
        self.request.session["otk"] = {
            "code": diagnosis_code,
            "expiry": expiry.timestamp(),
        }

        return self.render_to_response(
            {
                "code": diagnosis_code,
                "expiry": expiry,
                "sms_enabled": request.user.province.sms_enabled,
            }
        )

    def limit_reached(self):
        logger.error(
            f"User {self.request.user.email} has hit the limit of {settings.COVID_KEY_MAX_PER_USER} keys per 24h."
        )
        return render(self.request, "covid_key/locked.html", status=403)


class OtkSmsView(PermissionRequiredMixin, FormView, SessionTemplateView):
    form_class = OtkSmsForm
    template_name = "covid_key/otk_sms.html"
    permission_required = ["sms_enabled"]

    def __init__(self):
        super().__init__()
        self.phone_number = None

    def handle_no_permission(self):
        """
        Override here to redirect back to start when users are from
        a province that disallows SMS
        """
        return redirect(reverse_lazy("landing"))

    def get_success_url(self):
        return reverse_lazy("otk_sms_sent", kwargs={"phone_number": self.phone_number})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["code"] = self.request.session.get("otk")["code"]
        return context

    def form_valid(self, form):
        self.phone_number = str(form.cleaned_data.get("phone_number"))
        form.send_sms(self.request.LANGUAGE_CODE, self.request.session.get("otk"))
        return super().form_valid(form)


class OtkSmsSentView(PermissionRequiredMixin, FormView, SessionTemplateView):
    form_class = OtkSmsSentForm
    template_name = "covid_key/otk_sms_sent.html"
    permission_required = ["sms_enabled"]

    def __init__(self):
        super().__init__()
        self.redirect_choice = "landing"

    def handle_no_permission(self):
        """
        Override here to redirect back to start when users are from
        a province that disallows SMS
        """
        return redirect(reverse_lazy("landing"))

    def get_success_url(self):
        return reverse_lazy(self.redirect_choice)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["code"] = self.request.session.get("otk")["code"]
        context["phone_number"] = self.kwargs["phone_number"]
        return context

    def form_valid(self, form):
        self.redirect_choice = form.cleaned_data.get("redirect_choice")
        return super().form_valid(form)
