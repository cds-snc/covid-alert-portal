from urllib.parse import unquote, urlparse
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    DeleteView,
    TemplateView,
    DetailView,
)
from django.views.generic.edit import UpdateView

from django.contrib import messages
from django.urls import reverse_lazy
from django_otp import DEVICE_ID_SESSION_KEY
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.expressions import RawSQL
from django.utils.translation import LANGUAGE_SESSION_KEY, check_for_language
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponseRedirect
from django.urls import translate_url

from otp_yubikey.models import RemoteYubikeyDevice

from portal.mixins import ThrottledMixin, Is2FAMixin, IsAdminMixin
from invitations.models import Invitation
from axes.models import AccessAttempt

from .utils import generate_2fa_code
from .utils.invitation_adapter import user_signed_up
from .models import HealthcareUser, HealthcareFailedAccessAttempt
from .mixins import (
    EditPasswordMixin,
    ProvinceAdminViewMixin,
    ProvinceAdminEditMixin,
    ProvinceAdminDeleteMixin,
)
from .forms import (
    SignupForm,
    SignupForm2fa,
    Healthcare2FAForm,
    HealthcareInviteForm,
    HealthcarePasswordResetForm,
    Resend2FACodeForm,
    YubikeyDeviceCreateForm,
    YubikeyVerifyForm,
)


class YubikeyVerifyView(FormView):
    form_class = YubikeyVerifyForm
    template_name = "profiles/yubikey_verify.html"
    success_url = reverse_lazy("start")

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy("login"))

        if request.user.is_verified():
            return redirect(reverse_lazy("start"))

        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        device = self.request.user.remoteyubikeydevice_set.first()
        # Pass the device to the form
        kwargs.update({"device": device})
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        device = RemoteYubikeyDevice.objects.filter(user=self.request.user).first()
        self.request.user.otp_device = device
        self.request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id

        return response


class YubikeyCreateView(CreateView):
    form_class = YubikeyDeviceCreateForm
    template_name = "profiles/yubikey_create.html"

    def _check_yubikey_exists_for_user(self, user):
        return True if RemoteYubikeyDevice.objects.filter(user=user).first() else False

    def get(self, request, *args, **kwargs):
        # Enforce 1 yubikey per user
        if self._check_yubikey_exists_for_user(self.request.user):
            return redirect(self.get_success_url())

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("user_profile", kwargs={"pk": self.request.user.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add the currently logged user to the form
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class YubikeyDeleteView(Is2FAMixin, DeleteView):
    model = RemoteYubikeyDevice
    template_name = "profiles/yubikey_delete.html"

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        # If the user logged in with his yubikey in this session, he wont be verified anymore
        # So we need to send him a new SMS
        if request.user.is_verified() is False or isinstance(
            request.user.otp_device, RemoteYubikeyDevice
        ):
            generate_2fa_code(self.request.user)
        return response

    def get_success_url(self):
        return reverse_lazy("user_profile", kwargs={"pk": self.request.user.id})


class SignUpView(FormView):
    form_class = SignupForm
    template_name = "profiles/signup.html"

    def get_success_url(self):
        return reverse_lazy("signup-2fa")

    def get(self, request, *args, **kwargs):
        invited_email = self.request.session.get("account_verified_email", None)

        # if session variable or invitation is missing, redirect to "expired" page
        if not invited_email or not Invitation.objects.filter(
            email__iexact=invited_email
        ):
            return redirect("invite_expired")

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
        user = authenticate(
            request=self.request,
            username=form.cleaned_data.get("email"),
            password=form.cleaned_data.get("password1"),
        )
        user_signed_up.send(sender=user.__class__, request=self.request, user=user)
        login(self.request, user)
        

        # delete matching access attempts for this user
        AccessAttempt.objects.filter(username=user.email).delete(),
        HealthcareFailedAccessAttempt.objects.filter(username=user.email).delete()

        return super(SignUpView, self).form_valid(form)

class SignUp2FAView(LoginRequiredMixin, FormView):
    form_class = SignupForm2fa
    template_name = "profiles/signup2fa.html"

    def get_success_url(self):
        return "{}?next={}".format(reverse_lazy("login-2fa"), reverse_lazy("welcome"))

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        existing_user = HealthcareUser.objects.get(pk=self.request.user.id)
        existing_user.phone_number = form.instance.phone_number
        existing_user.save()

        generate_2fa_code(self.request.user)

        return super(SignUp2FAView, self).form_valid(form)

class Login2FAView(LoginRequiredMixin, FormView):
    form_class = Healthcare2FAForm
    template_name = "profiles/2fa.html"

    def get_success_url(self):
        next_url = self.request.GET.get("next", None)

        # don't want to allow arbitrary "nexts" here, so hardcode the welcome page
        if next_url and "welcome" in next_url:
            return reverse_lazy("welcome")

        return reverse_lazy("start")

    def get(self, request, *args, **kwargs):
        if request.user.is_verified():
            return redirect(reverse_lazy("start"))

        if request.user.remoteyubikeydevice_set.first() is not None:
            return redirect(reverse_lazy("yubikey_verify"))

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if settings.DEBUG:
            sms_device = self.request.user.notifysmsdevice_set.last()
            initial["code"] = sms_device.token
        return initial

    def form_valid(self, form):
        code = form.cleaned_data.get("code")
        devices = self.request.user.notifysmsdevice_set.all()
        being_throttled = False
        for device in devices:
            # let's check if the user is being throttled
            verified_allowed, errors_details = device.verify_is_allowed()
            if verified_allowed is False:
                being_throttled = True

            # Even though we know the device is being throttled, we still need to test it
            # If not, the throttling will never get increased for this device
            if device.verify_token(code):
                self.request.user.otp_device = device
                self.request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id

        if self.request.user.otp_device is None:
            # Just in case one of the device is throttled but another one
            # was verified
            if being_throttled:
                form.add_error("code", _("Please try again later."))

            if form.has_error("code") is False:
                form.add_error("code", _("You entered the wrong code."))

        if form.has_error("code"):
            return super().form_invalid(form)

        return super().form_valid(form)


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


class InvitationView(Is2FAMixin, IsAdminMixin, ThrottledMixin, FormView):
    form_class = HealthcareInviteForm
    template_name = "invitations/templates/invite.html"
    success_url = reverse_lazy("invite_complete")
    throttled_model = Invitation
    throttled_limit = settings.MAX_INVITATIONS_PER_PERIOD
    throttled_time_range = settings.MAX_INVITATIONS_PERIOD_SECONDS
    throttled_lookup_user_field = "inviter"
    throttled_lookup_date_field = "created"

    def form_valid(self, form):
        # Pass user to invite, save the invite to the DB, and return it
        invite = form.save(user=self.request.user)
        if not settings.TESTING:
            # Don't actually send the email during tests
            invite.send_invitation(
                self.request,
                scheme=self.request.scheme,
                language=get_language(),
            )
        self.request.session["invite_email"] = invite.email
        return super().form_valid(form)

    def limit_reached(self):
        return render(self.request, "invitations/templates/locked.html", status=403)


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
        queryset = HealthcareUser.objects.filter(province=self.request.user.province)

        # don't return superusers when an admin user makes the request
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_superuser=False)

        return queryset.annotate(
            current_user_email=RawSQL("email = %s", (self.request.user.email,))
        ).order_by("-current_user_email", "-is_admin")


class UserProfileView(Is2FAMixin, ProvinceAdminViewMixin, DetailView):
    model = HealthcareUser

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        healthcareuser = context["healthcareuser"]

        if healthcareuser.is_superuser:
            context["yubikey"] = RemoteYubikeyDevice.objects.filter(
                user=healthcareuser
            ).first()

        # True if this is an admin account viewing another admin account
        context["view_only"] = (
            healthcareuser.id != self.request.user.id
            and (not self.request.user.is_superuser)
            and healthcareuser.is_admin
        )
        return context


class HealthcareUserEditView(Is2FAMixin, ProvinceAdminEditMixin, UpdateView):
    model = HealthcareUser
    success_url = reverse_lazy("user_profile")

    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        initial["name"] = user.name
        return initial

    def get_success_url(self):
        return reverse_lazy("user_profile", kwargs={"pk": self.kwargs.get("pk")})


class HealthcarePasswordResetView(PasswordResetView):
    form_class = HealthcarePasswordResetForm

    def post(self, *args, **kwargs):
        base_url = self.request.build_absolute_uri("/")
        self.extra_email_context = {
            "base_url": base_url[:-1],  # remove the trailing slash
            "language": get_language(),
        }

        return super().post(*args, **kwargs)


class HealthcarePasswordChangeView(Is2FAMixin, EditPasswordMixin, PasswordChangeView):
    def get_success_url(self):
        return reverse_lazy("user_profile", kwargs={"pk": self.kwargs.get("pk")})


class UserDeleteView(Is2FAMixin, ProvinceAdminDeleteMixin, DeleteView):
    model = HealthcareUser
    context_object_name = "profile_user"
    success_url = reverse_lazy("profiles")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.add_message(
            request,
            messages.SUCCESS,
            _("You deleted the account for ‘%(email)s’.")
            % {"email": self.object.email},
        )
        # This wont crash if no object is returned from the filtered query
        Invitation.objects.filter(email=self.object.email).delete()
        return response


def redirect_after_timed_out(request):
    messages.add_message(
        request,
        messages.INFO,
        _("Your session timed out. Log in again to continue using the portal."),
        "logout",
    )
    return redirect(reverse_lazy("login"))


def password_reset_complete(request):
    if request.user.remoteyubikeydevice_set.first() is not None:
        return redirect(reverse_lazy("yubikey_verify"))
    else:
        generate_2fa_code(request.user)
        return redirect(reverse_lazy("login-2fa"))


def switch_language(request):
    current_lang = request.LANGUAGE_CODE
    lang = "en"
    if current_lang == "en":
        lang = "fr"

    if check_for_language(lang) is False:
        # Make sure the lang has been enabled in the config. If not, default to en
        lang = "en"

    # Take the referer by default
    next_url = urlparse(request.META.get("HTTP_REFERER"))
    # but if a ?next_url has been provided, let's make sure it's clean

    next_url = next_url.path and unquote(next_url.path)
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        # if it is not clean, let's default to /
        next_url = "/"

    root_domain = ""
    if settings.URL_DUAL_DOMAINS:
        root_domain = (
            settings.URL_FR_PRODUCTION if lang == "fr" else settings.URL_EN_PRODUCTION
        )

    next_url = root_domain + translate_url(next_url, lang)
    response = HttpResponseRedirect(next_url)

    if hasattr(request, "session"):
        request.session[LANGUAGE_SESSION_KEY] = lang

    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response
