from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from profiles.models import HealthcareUser
from django.views.generic import View, ListView

from django.urls import reverse_lazy
from django.views import generic

from .forms import SignupForm, HealthcareUserEditForm


class HomePageView(ListView):
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


class UserEdit(generic.UpdateView):
    model = HealthcareUser
    form_class = HealthcareUserEditForm
    template_name = 'profiles/user_edit.html'

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
