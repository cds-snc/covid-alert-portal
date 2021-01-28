from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render


from .models import Registrant


class RegistrantCreate(CreateView):
    model = Registrant
    fields = ["email"]
    template_name = "register/registrant_create.html"

    def get_success_url(self):
        return reverse_lazy("register:name", kwargs={"pk": self.object.pk})


class RegistrantUpdate(UpdateView):
    model = Registrant
    fields = ["name"]
    success_url = reverse_lazy("register:confirmation")
    template_name = "register/registrant_create.html"


class RegistrantListView(ListView):
    model = Registrant


class RegisterStartPageView(TemplateView):
    template_name = "register/start.html"


class RegisterConfirmationPageView(TemplateView):
    template_name = "register/confirmation.html"
