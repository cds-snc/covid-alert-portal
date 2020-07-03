import requests
import os
import sys


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView

from django.utils import timezone
from .forms import SignupForm
from django.contrib import messages
from django.urls import reverse_lazy


class SignUpView(FormView):
    form_class = SignupForm
    template_name = "profiles/signup.html"
    success_url = reverse_lazy("start")

    def get_initial(self):
        return {"email": self.request.session.get("account_verified_email", None)}

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Account created successfully")
        return super(SignUpView, self).form_valid(form)


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
