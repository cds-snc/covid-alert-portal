import requests
import os
import sys


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, ListView, View, DeleteView, TemplateView
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.decorators import otp_required

from invitations.models import Invitation

from .models import HealthcareUser
from .mixins import (
    IsAdminMixin,
    ProvinceAdminDeleteMixin,
    Is2FAMixin,
    ProvinceAdminManageMixin,
)
from .forms import (
    SignupForm,
    Healthcare2FAForm,
    HealthcareInviteForm,
    Resend2FACodeForm,
)


class SignUpView(FormView):
    form_class = SignupForm
    template_name = "profiles/signup.html"
    success_url = reverse_lazy("start")

    def get(self, request, *args, **kwargs):
        invited_email = self.request.session.get("account_verified_email", None)

        # redirect to login page if there's no invited email in the session
        if not invited_email:
            messages.warning(self.request, _("No invited email in session"))
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
        messages.success(self.request, _("Account created successfully"))

        return super(SignUpView, self).form_valid(form)


class Login2FAView(FormView, LoginRequiredMixin):
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


class Resend2FAView(FormView, LoginRequiredMixin):
    form_class = Resend2FACodeForm
    template_name = "profiles/2fa-resend.html"
    success_url = reverse_lazy("login-2fa")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        is_valid = super().form_valid(form)
        if is_valid:
            messages.success(self.request, _("Security code has been sent."))

        return is_valid


class InviteView(LoginRequiredMixin, Is2FAMixin, IsAdminMixin, FormView):
    form_class = HealthcareInviteForm
    template_name = "invitations/templates/invite.html"
    success_url = reverse_lazy("invite_complete")

    def form_valid(self, form):
        # Pass user to invite, save the invite to the DB, and return it
        invite = form.save(user=self.request.user)
        invite.send_invitation(self.request)
        messages.success(
            self.request, "Invitation sent to “{}”".format(invite.email), "invite"
        )
        self.request.session["invite_email"] = invite.email
        return super().form_valid(form)


class InviteCompleteView(LoginRequiredMixin, Is2FAMixin, IsAdminMixin, TemplateView):
    template_name = "invitations/templates/invite_complete.html"


class ProfilesView(LoginRequiredMixin, Is2FAMixin, IsAdminMixin, ListView):
    def get_queryset(self):
        return HealthcareUser.objects.filter(
            province=self.request.user.province
        ).order_by("-is_admin")


class UserProfileView(LoginRequiredMixin, Is2FAMixin, ProvinceAdminManageMixin, View):
    def get(self, request, pk):
        profile_user = get_object_or_404(HealthcareUser, pk=pk)
        return render(
            request, "profiles/user_profile.html", {"profile_user": profile_user}
        )


class UserDeleteView(
    LoginRequiredMixin, Is2FAMixin, ProvinceAdminDeleteMixin, DeleteView
):
    model = HealthcareUser
    context_object_name = "profile_user"
    success_url = reverse_lazy("profiles")


@login_required
@otp_required
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
