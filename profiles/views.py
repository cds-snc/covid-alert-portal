import requests
import os
import sys

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from profiles.models import HealthcareUser
from django.views.generic import View, ListView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic

from .forms import SignupForm, HealthcareUserEditForm


class UserListView(LoginRequiredMixin, ListView):
    model = HealthcareUser

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, pk):
        try:
            user = HealthcareUser.objects.get(id=pk)
        except:
            user = None

        context = {
            "viewed_user": user
        }

        return render(request, "profiles/user_profile.html", context)


class UserEdit(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = HealthcareUser
    form_class = HealthcareUserEditForm
    template_name = 'profiles/user_edit.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def test_func(self):
        # the logged-in user should be the same as the user ID
        # the id is an int, so we cast it to a string
        return str(self.request.user.id) == self.kwargs['pk']

    def get_initial(self):
        user = get_object_or_404(HealthcareUser, pk=self.kwargs['pk'])
        # pre-populate the form
        return {
            'email': user.email,
            'name': user.name,
            'language': user.language,
        }

    def get_success_url(self):
        return reverse_lazy('user_profile', kwargs={'pk': self.kwargs['pk']})

@login_required
def code(request):
    token = os.getenv("API_AUTHORIZATION")

    diagnosis_code = '0000 0000'

    if token:
        try:
            r = requests.post(os.getenv("API_ENDPOINT"), headers={'Authorization': 'Bearer ' + token})
            r.raise_for_status()  # If we don't get a valid response, throw an exception
            diagnosis_code = r.text
        except requests.exceptions.HTTPError as err:
            sys.stderr.write("Received " + str(r.status_code) + " " + err.response.text)
            sys.stderr.flush()
        except requests.exceptions.RequestException as err:
            sys.stderr.write('Something went wrong')
            sys.stderr.flush()

    # Split up the code with a space in the middle so it looks like this: 1234 5678
    diagnosis_code = diagnosis_code[0:4] + ' ' + diagnosis_code[4:8]

    return render(request, 'profiles/code.html', {'code': diagnosis_code})
