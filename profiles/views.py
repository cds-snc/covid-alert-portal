import requests
import os
import sys


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from invitations.models import Invitation

from .models import HealthcareUser
from .forms import SignupForm, HealthcareInviteForm


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


class InviteView(FormView):
    form_class = HealthcareInviteForm
    template_name = "invitations/templates/invite.html"
    success_url = reverse_lazy("invite_complete")

    def get_initial(self):
        # preload the invite form with the id of the inviter
        return {"inviter": self.request.user.id}

    def form_valid(self, form):
        # Save the invite to the DB and return it
        invite = form.save()
        invite.send_invitation(self.request)
        messages.success(
            self.request, "Invitation sent to “{}”".format(invite.email), "invite"
        )
        self.request.session["invite_email"] = invite.email
        return super().form_valid(form)


class ProfilesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    def test_func(self):
        # if superuser, return manage_accounts page
        if self.request.user.is_superuser or self.request.user.is_admin:
            return True

        return False

    def get_queryset(self):
        return HealthcareUser.objects.filter(
            province=self.request.user.province
        ).order_by("-is_admin")


class ProvinceAdminManageMixin(UserPassesTestMixin):
    def test_func(self):
        # 404 if bad user ID
        profile_user = get_object_or_404(HealthcareUser, pk=self.kwargs["pk"])

        # if superuser, return profile
        if self.request.user.is_superuser:
            return True

        # if same user, return profile
        if self.request.user.id == int(profile_user.id):
            return True

        # if admin user from same province, return profile
        if (
            self.request.user.is_admin
            and self.request.user.province.id == profile_user.province.id
        ):
            return True

        return False


class UserProfileView(LoginRequiredMixin, ProvinceAdminManageMixin, View):
    def get(self, request, pk):
        profile_user = get_object_or_404(HealthcareUser, pk=pk)
        return render(
            request, "profiles/user_profile.html", {"profile_user": profile_user}
        )


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
