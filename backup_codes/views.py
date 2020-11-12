from django.views.generic import ListView, FormView

from invitations.models import Invitation
from profiles.models import HealthcareUser

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp import DEVICE_ID_SESSION_KEY

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.conf import settings

from waffle.mixins import WaffleSwitchMixin
from portal.mixins import Is2FAMixin

from backup_codes.forms import RequestBackupCodesForm

from django.utils.translation import gettext as _
from django.utils.functional import cached_property


class BackupCodeListView(WaffleSwitchMixin, Is2FAMixin, ListView):
    waffle_switch = "BACKUP_CODE"
    template_name = "backup_codes/backup_codes_list.html"
    context_object_name = "backup_code_list"

    def get(self, request, *args, **kwargs):
        if not get_user_static_device(self, self.request.user):
            return redirect(
                reverse_lazy("user_profile", kwargs={"pk": request.user.id})
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.recreate_backup_codes(request)
        return redirect(reverse_lazy("backup_codes"))

    def get_queryset(self):
        return get_user_static_device(self, self.request.user).token_set.all()

    def recreate_backup_codes(self, request):
        devices = get_user_static_device(self, request.user)
        if devices:
            devices.token_set.all().delete()
        else:
            devices = StaticDevice.objects.create(
                user=request.user, name="Static_Security_Codes"
            )
        for n in range(5):
            security_code = StaticToken.random_token()
            devices.token_set.create(token=security_code)


class RequestBackupCodes(WaffleSwitchMixin, LoginRequiredMixin, FormView):
    waffle_switch = "BACKUP_CODE"
    form_class = RequestBackupCodesForm
    template_name = "backup_codes/backup_codes_help.html"
    success_url = reverse_lazy("login-2fa")

    @cached_property
    def user_admin(self):
        if self.user_was_invited:
            invitation = Invitation.objects.filter(
                email__iexact=self.request.user.email
            ).first()
            if HealthcareUser.objects.filter(
                email__iexact=invitation.inviter.email
            ).exists():
                return invitation.inviter

        return dict(
            {"email": "assistance+healthcare@cds-snc.ca", "name": "Portal Super Admin"}
        )

    @cached_property
    def user_was_invited(self):
        return Invitation.objects.filter(email__iexact=self.request.user.email).exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add the currently logged user to the form
        kwargs["user"] = self.request.user
        kwargs["admin"] = self.user_admin
        return kwargs

    def form_valid(self, form):
        is_valid = super().form_valid(form)
        if is_valid:
            if settings.DEBUG:
                print(
                    f"DEBUG ONLY: Email message would have been sent to {form.admin.email} for {form.user.name} with {form.user.email} email address"
                )
            else:
                form.send_mail(self.request.LANGUAGE_CODE)

            logout(self.request)
            return redirect(reverse_lazy("backup_codes_contacted"))
        return is_valid


######################
# Functions used from the Profiles module for 2fa login.
######################


def get_user_static_device(self, user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, StaticDevice):
            return device


def get_user_backup_codes_count(self, user):
    devices = get_user_static_device(self, user)
    token_count = 0
    if devices:
        tokens = devices.token_set.all()
        token_count = tokens.count()
    return token_count


def verify_user_code(self, code, devices):
    being_throttled = False
    code_sucessful = False
    for device in devices:
        # let's check if the user is being throttled on the sms codes
        verified_allowed, errors_details = device.verify_is_allowed()
        if verified_allowed is False:
            being_throttled = True

        # Even though we know the device is being throttled, we still need to test it
        # If not, the throttling will never get increased for this device
        if device.verify_token(code):
            code_sucessful = True
            self.request.user.otp_device = device
            self.request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id

    return [code_sucessful, being_throttled]
