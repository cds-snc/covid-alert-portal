from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render

from waffle.mixins import WaffleSwitchMixin

from .models import Registrant, Location
from .forms import EmailForm, RegistrantNameForm
from collections import ChainMap

from formtools.wizard.views import NamedUrlSessionWizardView


class RegistrantEmailView(WaffleSwitchMixin, FormView):
    waffle_switch = "QR_CODES"
    form_class = EmailForm
    template_name = "register/registrant_email.html"

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        obj, created = Registrant.objects.get_or_create(
            email=email,
        )

        self._object = obj
        self.request.session["registrant_email"] = email

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("register:registrant_name", kwargs={"pk": self._object.pk})


class RegistrantNameView(WaffleSwitchMixin, UpdateView):
    waffle_switch = "QR_CODES"
    model = Registrant
    form_class = RegistrantNameForm
    # success_url = reverse_lazy("register:confirmation")
    template_name = "register/registrant_name.html"

    def get_success_url(self):
        return reverse_lazy(
            "register:location_step",
            kwargs={"pk": self.kwargs.get("pk"), "step": "category"},
        )


class RegisterStartPageView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/start.html"


TEMPLATES = {
    "category": "register/location_category.html",
    "name": "register/location_name.html",
    "address": "register/location_address.html",
    "contact": "register/location_contact.html",
    "summary": "register/summary.html",
}


class LocationWizard(NamedUrlSessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_step_url(self, step):
        return reverse(
            self.url_name, kwargs={"pk": self.kwargs.get("pk"), "step": step}
        )

    def get_context_data(self, form, **kwargs):
        context = super(LocationWizard, self).get_context_data(form=form, **kwargs)
        registrant = Registrant.objects.get(id=self.kwargs.get("pk"))
        context["form_data"] = self.get_all_cleaned_data
        context["registrant"] = registrant
        return context

    def done(self, form_list, form_dict, **kwargs):
        forms = [form.cleaned_data for form in form_list]
        location = dict(ChainMap(*forms))
        registrant = Registrant.objects.get(id=self.kwargs.get("pk"))
        print(location)

        obj, created = Location.objects.get_or_create(
            category=location["category"],
            name=location["name"],
            address=location["address"],
            address_2=location["address_2"],
            city=location["city"],
            province=location["province"],
            postal_code=location["postal_code"],
            contact_email=location["contact_email"],
            contact_phone=location["contact_phone"],
        )

        return render(
            self.request,
            "register/confirmation.html",
            {
                "registrant": registrant,
                "form_data": location,
            },
        )


class RegisterConfirmationPageView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registrant_email"] = self.request.session.get("registrant_email")
        return context
