import requests
import os
import sys


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy
from django.views import generic
from .forms import SignupForm
from portal import settings


def envs(request):

    context = {
        "DEBUG": settings.debug,
        "DJANGO_DEBUG": os.getenv("DJANGO_DEBUG"),
        "DJANGO_ENV": os.getenv("DJANGO_ENV"),
        "DOCKERFILE_ONLY": os.getenv("DOCKERFILE_ONLY"),
        "DOCKERFILE_HEROKUYML": os.getenv("DOCKERFILE_HEROKUYML"),
        "DOCKERFILE_APPJSON": os.getenv("DOCKERFILE_APPJSON"),
        "DOCKERFILE_HEROKUYML_APPJSON": os.getenv("DOCKERFILE_HEROKUYML_APPJSON"),
    }
    return render(request, "profiles/envs.html", {"context": context})


class SignUp(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    template_name = "profiles/signup.html"


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

    return render(request, "profiles/code.html", {"code": diagnosis_code})
