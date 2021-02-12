from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse

from waffle.mixins import WaffleSwitchMixin

from .models import Registrant, Location, EmailConfirmation
from .forms import EmailForm, RegistrantNameForm
from collections import ChainMap

from formtools.wizard.views import NamedUrlSessionWizardView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from datetime import datetime, timedelta


class RegistrantEmailView(WaffleSwitchMixin, FormView):
    waffle_switch = "QR_CODES"
    form_class = EmailForm
    template_name = "register/registrant_email.html"

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        confirm = EmailConfirmation.objects.create(email=email)
        url = reverse_lazy("register:email_confirm", kwargs={"pk": confirm.pk})
        print("LINK: " + str(url))
        # TODO: send email

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("register:email_submitted")


class RegistrantEmailSubmittedView(TemplateView):
    template_name = "register/registrant_email_submitted.html"


# TODO: Maybe this should be an UpdateView? (see below)
def confirm_email(request, pk):
    time_threshold = datetime.now() - timedelta(hours=24)

    try:
        confirm = EmailConfirmation.objects.get(id=pk, created__gt=time_threshold)
        request.session["registrant_email"] = confirm.email

        # TODO: Don't create the registrant object (just name/email set to session)
        registrant, created = Registrant.objects.get_or_create(email=confirm.email)

        confirm.delete()

        return redirect(
            reverse_lazy("register:registrant_name", kwargs={"pk": registrant.pk})
        )
    except (EmailConfirmation.DoesNotExist):
        return redirect(reverse_lazy("register:confirm_email_error"))


class RegistrantEmailConfirmError(TemplateView):
    template_name = "register/error.html"


class RegistrantNameView(WaffleSwitchMixin, UpdateView):
    waffle_switch = "QR_CODES"
    model = Registrant
    form_class = RegistrantNameForm
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
    waffle_switch = "QR_CODES"

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_step_url(self, step):
        return reverse(
            self.url_name, kwargs={"pk": self.kwargs.get("pk"), "step": step}
        )

    def get_context_data(self, form, **kwargs):
        context = super(LocationWizard, self).get_context_data(form=form, **kwargs)
        registrant = Registrant.objects.get(id=self.kwargs.get("pk"))
        context["form_data"] = self.get_all_cleaned_data()
        context["registrant"] = registrant
        return context

    def done(self, form_list, form_dict, **kwargs):
        forms = [form.cleaned_data for form in form_list]
        location = dict(ChainMap(*forms))

        Location.objects.create(
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

        return HttpResponseRedirect(
            reverse("register:confirmation", kwargs={"pk": self.kwargs.get("pk")})
        )


class RegisterConfirmationPageView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registrant_email"] = self.request.session.get("registrant_email")
        return context
