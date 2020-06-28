import requests
import os
import sys


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from .forms import SignupForm
from django.contrib import messages


def signup(request):
    if request.method == "POST":
        f = SignupForm(
            request.POST,
            initial={"email": request.session.get("account_verified_email", None)},
        )
        if f.is_valid():
            f.save()
            messages.success(request, "Account created successfully")
            return redirect("start")

    else:
        prepopulate = {}
        prepopulate["email"] = request.session.get("account_verified_email", None)
        f = SignupForm(initial=prepopulate)

    return render(request, "profiles/signup.html", {"form": f})


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
