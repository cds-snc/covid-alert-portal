import requests
import logging
from datetime import timedelta

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext as _
from django.views.generic import (
    FormView,
    ListView,
    DeleteView,
    TemplateView,
    DetailView,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.decorators import otp_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.expressions import RawSQL
from django.utils import timezone


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
from .utils import get_site_name

logger = logging.getLogger(__name__)


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
            "province": inviter.province.abbr,
        }

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Account created successfully"))
        # Let's login the user right now
        user = authenticate(
            request=self.request,
            username=form.cleaned_data.get("email"),
            password=form.cleaned_data.get("password1"),
        )
        login(self.request, user)
        email_device = user.emaildevice_set.create()
        self.request.session[DEVICE_ID_SESSION_KEY] = email_device.persistent_id
        self.request.session.save()

        return super(SignUpView, self).form_valid(form)


class Login2FAView(LoginRequiredMixin, FormView):
    form_class = Healthcare2FAForm
    template_name = "profiles/2fa.html"
    success_url = reverse_lazy("start")

    def get(self, request, *args, **kwargs):
        if request.user.is_verified():
            return redirect(reverse_lazy("code"))
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if settings.DEBUG:
            email_device = self.request.user.emaildevice_set.last()
            initial["code"] = email_device.token
        return initial

    def form_valid(self, form):
        code = form.cleaned_data.get("code")
        for device in self.request.user.emaildevice_set.all():
            if device.verify_token(code):
                self.request.user.otp_device = device
                self.request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id

        is_valid = super().form_valid(form)
        return is_valid


class Resend2FAView(LoginRequiredMixin, FormView):
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


class InvitationView(Is2FAMixin, IsAdminMixin, FormView):
    form_class = HealthcareInviteForm
    template_name = "invitations/templates/invite.html"
    success_url = reverse_lazy("invite_complete")

    def form_valid(self, form):
        # Pass user to invite, save the invite to the DB, and return it
        invite = form.save(user=self.request.user)
        current_site = get_current_site(self.request)
        subject_line = "{}{}".format(
            get_site_name(self.request), _(": Your portal account")
        )
        invite.send_invitation(
            self.request,
            scheme=self.request.scheme,
            http_host=current_site.domain,
            subject_line=subject_line,
        )
        messages.success(
            self.request, "Invitation sent to “{}”".format(invite.email), "invite"
        )
        self.request.session["invite_email"] = invite.email
        return super().form_valid(form)


class InvitationListView(Is2FAMixin, IsAdminMixin, ListView):
    template_name = "invitations/templates/invite_list.html"

    def get_queryset(self):
        return Invitation.objects.filter(
            inviter__province=self.request.user.province, accepted=False
        ).order_by("-sent")


class InvitationDeleteView(Is2FAMixin, IsAdminMixin, DeleteView):
    model = Invitation
    context_object_name = "invitation"
    success_url = reverse_lazy("invitation_list")
    template_name = "invitations/templates/invitation_confirm_delete.html"


class InvitationCompleteView(Is2FAMixin, IsAdminMixin, TemplateView):
    template_name = "invitations/templates/invite_complete.html"


class ProfilesView(Is2FAMixin, IsAdminMixin, ListView):
    def get_queryset(self):
        return (
            HealthcareUser.objects.filter(province=self.request.user.province)
            .annotate(
                current_user_email=RawSQL("email = %s", (self.request.user.email,))
            )
            .order_by("-current_user_email", "-is_admin")
        )


class UserProfileView(Is2FAMixin, ProvinceAdminManageMixin, DetailView):
    model = HealthcareUser


class UserDeleteView(Is2FAMixin, ProvinceAdminDeleteMixin, DeleteView):
    model = HealthcareUser
    context_object_name = "profile_user"
    success_url = reverse_lazy("profiles")


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
