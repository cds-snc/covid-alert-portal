import requests
import os
import sys


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY

from invitations.models import Invitation

from .models import HealthcareUser
from .forms import SignupForm, Healthcare2FAForm


class SignUpView(FormView):
    form_class = SignupForm
    template_name = "profiles/signup.html"
    success_url = reverse_lazy("start")

    def get(self, request, *args, **kwargs):
        invited_email = self.request.session.get("account_verified_email", None)

        # redirect to login page if there's no invited email in the session
        if not invited_email:
            messages.warning(self.request, "No invited email in session")
            return redirect("login")

        # redirect to login page if there's no Invitation for this email
        if not Invitation.objects.filter(email__iexact=invited_email):
            messages.error(
                self.request, "Invitation not found for {}".format(invited_email)
            )
            return redirect("login")

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        invited_email = self.request.session.get("account_verified_email", None)

        # get invite object and the admin user who sent the invite
        inviter_id = Invitation.objects.get(email__iexact=invited_email).inviter_id
        inviter = HealthcareUser.objects.get(id=inviter_id)

        # preload the signup form with the email and the province of the admin
        return {
            "email": invited_email,
            "province": inviter.province.name,
        }

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Account created successfully")

        return super(SignUpView, self).form_valid(form)


class Login2FAView(FormView):
    form_class = Healthcare2FAForm
    template_name = "profiles/2fa.html"
    success_url = reverse_lazy("start")

    def form_valid(self, form):
        code = form.cleaned_data.get("code")
        for device in self.request.user.emaildevice_set.all():
            if device.verify_token(code):
                self.request.user.otp_device = device
                self.request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id

        is_valid = super().form_valid(form)
        return is_valid


@login_required
def code(request):
    token = os.getenv("API_AUTHORIZATION")

    diagnosis_code = "0000 0000"

    if token:
        try:
            r = requests.post(
                os.getenv("API_ENDPOINT"), headers={"Authorization": "Bearer " + token}
            )
            r.raise_for_status()  # If we don't get a valid response, throw an exception
            diagnosis_code = r.text
        except requests.exceptions.HTTPError as err:
            sys.stderr.write("Received " + str(r.status_code) + " " + err.response.text)
            sys.stderr.flush()
        except requests.exceptions.RequestException as err:
            sys.stderr.write("Something went wrong", err)
            sys.stderr.flush()

    # Split up the code with a space in the middle so it looks like this: 1234 5678
    diagnosis_code = diagnosis_code[0:4] + " " + diagnosis_code[4:8]

    return render(
        request, "profiles/code.html", {"code": diagnosis_code, "time": timezone.now()}
    )
