from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse

from .models import Registrant, Location, EmailConfirmation
from .forms import EmailForm, RegistrantNameForm, ContactUsForm
from collections import ChainMap
from django.utils.translation import gettext as _
from formtools.wizard.views import NamedUrlSessionWizardView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from datetime import datetime, timedelta
import pytz
from django.contrib import messages
from .forms import location_choices
from .utils import get_signed_qrcode
from profiles.models import HealthcareProvince


class RegistrantEmailView(FormView):
    form_class = EmailForm
    template_name = "register/registrant_email.html"
    success_url = reverse_lazy("register:email_submitted")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        self.submitted_email = email
        confirm = EmailConfirmation.objects.create(email=email)

        # get the base url and strip the trailing slash
        base_url = self.request.build_absolute_uri("/")[:-1]

        # build the email confirmation link
        url = base_url + reverse(
            "register:email_confirm",
            kwargs={"pk": confirm.pk},
        )

        form.send_mail(self.request.LANGUAGE_CODE, email, url)
        self.request.session["submitted_email"] = self.submitted_email

        return super().form_valid(form)


class RegistrantEmailSubmittedView(TemplateView):
    template_name = "register/registrant_email_submitted.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.get("submitted_email"):
            return redirect(reverse_lazy("register:registrant_email"))
        return super(RegistrantEmailSubmittedView, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submitted_email"] = self.request.session.get("submitted_email")
        del self.request.session["submitted_email"]
        return context


def confirm_email(request, pk):
    try:
        # Confirmation tokens are only valid for 24hrs
        time_threshold = pytz.utc.localize(datetime.now() - timedelta(hours=24))

        confirm = EmailConfirmation.objects.get(id=pk)

        # Expired token
        if confirm.created < time_threshold:
            print("Error: Email verification token has expired")
            return redirect(reverse_lazy("register:confirm_email_error"))

        # Create the Registrant
        registrant, created = Registrant.objects.get_or_create(email=confirm.email)

        # Save to session
        request.session["registrant_id"] = str(registrant.id)
        request.session["registrant_email"] = registrant.email

        # Delete the confirmation
        confirm.delete()

        messages.add_message(
            request, messages.SUCCESS, _("You've confirmed your email address.")
        )

        return redirect(reverse_lazy("register:registrant_name"))
    except (EmailConfirmation.DoesNotExist):
        return redirect(reverse_lazy("register:confirm_email_error"))


class RegistrantNameView(UpdateView):
    model = Registrant
    form_class = RegistrantNameForm
    template_name = "register/registrant_name.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.get("registrant_id"):
            messages.add_message(
                self.request,
                messages.ERROR,
                _("There has been an error, you need to confirm your email address"),
            )
            return redirect("register:registrant_email")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return Registrant.objects.get(pk=self.request.session["registrant_id"])

    def get_success_url(self):
        return reverse_lazy(
            "register:location_step",
            kwargs={"step": "address"},
        )


TEMPLATES = {
    "address": "register/location_address.html",
    "unavailable": "register/location_unavailable.html",
    "category": "register/location_category.html",
    "name": "register/location_name.html",
    "contact": "register/location_contact.html",
    "summary": "register/summary.html",
    "success": "register/success.html",
}


def check_for_province(wizard):
    data = wizard.get_cleaned_data_for_step("address") or {}
    provinces = HealthcareProvince.objects.filter(qr_code_enabled=True)
    provinces_values = provinces.values_list("abbr", flat=True)
    provinces_list = list(provinces_values)

    return data.get("province") not in provinces_list


class LocationWizard(NamedUrlSessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def render(self, form=None, **kwargs):
        if not self.request.session.get("registrant_id"):
            messages.add_message(
                self.request,
                messages.ERROR,
                _("There has been an error, you need to confirm your email address"),
            )
            return redirect(reverse_lazy("register:registrant_email"))
        return super().render(form, **kwargs)

    def get_step_url(self, step):
        return reverse(self.url_name, kwargs={"step": step})

    def get_context_data(self, form, **kwargs):
        context = super(LocationWizard, self).get_context_data(form=form, **kwargs)
        registrant = Registrant.objects.get(id=self.request.session["registrant_id"])
        context["form_data"] = self.get_all_cleaned_data()
        context["registrant"] = registrant
        if "category" in context["form_data"]:
            context["form_data"]["category"] = dict(location_choices)[
                context["form_data"]["category"]
            ]

        return context

    def done(self, form_list, form_dict, **kwargs):
        forms = [form.cleaned_data for form in form_list]
        data = dict(ChainMap(*forms))

        location, created = Location.objects.get_or_create(
            name=data["name"],
            address=data["address"],
            address_2=data["address_2"],
            city=data["city"],
            province=data["province"],
            postal_code=data["postal_code"],
        )

        location.category = data["category"]
        if location.category == "other":
            location.category_description = data["category_description"]
        else:
            location.category_description = ""
        location.contact_name = data["contact_name"]
        location.contact_email = data["contact_email"]
        location.contact_phone = data["contact_phone"]
        location.save()

        base_url = self.request.build_absolute_uri("/")[:-1]
        poster_url = "{base_url}{poster_url}".format(
            base_url=base_url,
            poster_url=reverse("register:poster_view", kwargs={"pk": location.pk}),
        )
        print(poster_url)
        self.request.session["poster_url"] = poster_url

        # Generate PDF and send

        return HttpResponseRedirect(reverse("register:confirmation"))


class PosterView(TemplateView):
    template_name = "register/poster.svg"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = Location.objects.get(id=self.kwargs["pk"])

        qr_code = get_signed_qrcode(location)

        context["qr_code"] = qr_code
        context["name"] = location.name
        context["address"] = location.address
        context["address_details"] = "{city}, {province} {postal_code}".format(
            city=location.city,
            province=location.province,
            postal_code=location.postal_code,
        )
        return context


class RegisterConfirmationPageView(TemplateView):
    template_name = "register/confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.get("registrant_id"):
            messages.add_message(
                self.request,
                messages.ERROR,
                _("There has been an error, you need to confirm your email address"),
            )
            return redirect("register:registrant_email")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registrant_email"] = self.request.session.get("registrant_email")
        return context


class ContactUsPageView(FormView):
    template_name = "register/contact_us.html"
    form_class = ContactUsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy("register:success")


class QRSupportPageView(TemplateView):
    template_name = "register/qr_support_page.html"


class ResendEmailView(TemplateView):
    template_name = "register/resend_email.html"
