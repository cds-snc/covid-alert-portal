from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render

from .models import Registrant
from .forms import RegistrantCreateForm, RegistrantNameForm


class RegistrantCreate(CreateView):
    form_class = RegistrantCreateForm
    template_name = "register/registrant_create.html"

    def get_success_url(self):
        return reverse_lazy("register:name", kwargs={"pk": self.object.pk})


class RegistrantUpdate(UpdateView):
    model = Registrant
    form_class = RegistrantNameForm
    success_url = reverse_lazy("register:confirmation")
    template_name = "register/registrant_create.html"


class RegisterStartPageView(TemplateView):
    template_name = "register/start.html"


class RegisterConfirmationPageView(TemplateView):
    template_name = "register/confirmation.html"
