from django.shortcuts import render
from profiles.models import HealthcareUser
from django.views.generic import View, ListView

from django.urls import reverse_lazy
from django.views import generic

from .forms import SignupForm


class HomePageView(ListView):
    model = HealthcareUser


class UserProfileView(View):
    def get(self, request, user_id):

        try:
            user = HealthcareUser.objects.get(id=user_id)
        except:
            user = None

        context = {
            "viewed_user": user
        }

        return render(request, "user_profile.html", context)


class SignUp(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('profiles:login')
    template_name = 'profiles/signup.html'
