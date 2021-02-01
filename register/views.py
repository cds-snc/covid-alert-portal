from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse

from waffle.mixins import WaffleSwitchMixin


from .models import Registrant
from .forms import (
    EmailForm,
    RegistrantNameForm,
    LocationCategoryForm,
    LocationNameForm,
    LocationAddressForm,
    LocationContactForm,
)

from django.http import HttpResponseRedirect
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
        return reverse_lazy("register:name", kwargs={"pk": self._object.pk})


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
}


class LocationWizard(NamedUrlSessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_step_url(self, step):
        return reverse(
            self.url_name, kwargs={"pk": self.kwargs.get("pk"), "step": step}
        )

    def done(self, form_list, form_dict, **kwargs):
        # do_something_with_the_form_data(form_list)
        print(form_dict)
        return HttpResponseRedirect("/register/confirmation")


class RegisterLocationCategoryView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/location_category.html"


class RegisterConfirmationPageView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registrant_email"] = self.request.session.get("registrant_email")
        return context
