import requests
import os
import sys


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone

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


class ProfilesView(ListView):
    model = HealthcareUser


class UserProfileView(View):
    def get(self, request, pk):
        try:
            user = HealthcareUser.objects.get(id=pk)
        except:
            user = None

        context = {"viewed_user": user}

        return render(request, "profiles/user_profile.html", context)


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
