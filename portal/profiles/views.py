from django.shortcuts import render
from profiles.models import HealthcareUser
from django.views.generic import View, ListView


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