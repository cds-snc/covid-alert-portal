import requests
import os


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from profiles.models import HealthcareUser
from django.views.generic import View, ListView

from django.urls import reverse_lazy
from django.views import generic

from .forms import SignupForm, HealthcareUserEditForm


class StartPageView(ListView):
    model = HealthcareUser


class UserProfileView(View):
    def get(self, request, pk):
        try:
            user = HealthcareUser.objects.get(id=pk)
        except:
            user = None

        context = {
            "viewed_user": user
        }

        return render(request, "profiles/user_profile.html", context)


class SignUp(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'profiles/signup.html'


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


def code(request):
    token = os.getenv("AUTHORIZATION")
    print(token)
    auth_header = {'Authorization': 'Bearer ' + token}  # This will go in an Env variable at some point
    r = requests.post(os.getenv("ENDPOINT"), headers=auth_header)
    code = r.text
    code = code[0:4] + ' ' + code[4:8]
    context = {'code': code}
    return render(request, 'code/code.html', context)
