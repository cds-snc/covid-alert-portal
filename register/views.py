from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse

from .models import Registrant, Location, EmailConfirmation
from .forms import EmailForm, ContactUsForm
from collections import ChainMap
from django.utils.translation import gettext as _
from formtools.wizard.views import NamedUrlSessionWizardView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from datetime import datetime, timedelta
import pytz
from django.contrib import messages
from .forms import location_choices, send_email
from .utils import get_pdf_poster, get_encoded_poster
from profiles.models import HealthcareProvince
from django.http import FileResponse
from django.conf import settings


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

        send_email(
            email,
            {
                "verification_link": url,
            },
            settings.REGISTER_EMAIL_CONFIRMATION_TEMPLATE_ID.get(
                self.request.LANGUAGE_CODE or "en"
            ),
        )

        self.request.session["submitted_email"] = self.submitted_email

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()

        try:
            submitted = self.request.session["submitted_email"]
            initial["email"] = submitted
        except KeyError:
            initial["email"] = ""

        return initial


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

        return redirect(
            reverse_lazy(
                "register:location_step",
                kwargs={"step": "category"},
            )
        )
    except (EmailConfirmation.DoesNotExist):
        return redirect(reverse_lazy("register:confirm_email_error"))


TEMPLATES = {
    "category": "register/location_category.html",
    "name": "register/location_name.html",
    "address": "register/location_address.html",
    "unavailable": "register/location_unavailable.html",
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

        # Save the location (matching duplicates)
        location, created = Location.objects.get_or_create(
            name=data["name"],
            address=data["address"],
            address_2=data["address_2"],
            city=data["city"],
            province=data["province"],
            postal_code=data["postal_code"],
        )

        # Only set the category description if "other" selected
        location.category = data["category"]
        if location.category == "other":
            location.category_description = data["category_description"]
        else:
            location.category_description = ""

        # Update contact info
        location.contact_name = data["contact_name"]
        location.contact_email = data["contact_email"]
        location.contact_phone = data["contact_phone"]
        location.contact_phone_ext = data["contact_phone_ext"]
        location.save()

        # Save location id to session for next step
        # (@TODO: should we just put it on the url?)
        self.request.session["location_id"] = str(location.id)

        # Generate PDF and send
        en_poster = get_encoded_poster(location, "en")
        fr_poster = get_encoded_poster(location, "fr")

        to_email = self.request.session["registrant_email"]

        send_email(
            to_email,
            {
                "location_name": location.name,
                "english_poster": {
                    "file": en_poster,
                    "filename": "poster-en.pdf",
                    "sending_method": "attach",
                },
                "french_poster": {
                    "file": fr_poster,
                    "filename": "poster-fr.pdf",
                    "sending_method": "attach",
                },
            },
            settings.POSTER_LINKED_EMAIL_TEMPLATE_ID.get(
                self.request.LANGUAGE_CODE or "en"
            ),
        )

        return HttpResponseRedirect(reverse("register:confirmation"))


def download_poster(request, pk, lang):
    location = Location.objects.get(id=pk)
    filename = "poster-{lang}.pdf".format(lang=lang)
    poster = get_pdf_poster(location, lang)

    return FileResponse(poster, as_attachment=True, filename=filename)


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
        context["location_id"] = self.request.session.get("location_id")
        return context


subject = {"get_help": "Help", "give_feedback": "Feedback", "something_else": "Other"}


class ContactUsPageView(FormView):
    template_name = "register/contact_us.html"
    form_class = ContactUsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy("register:success")

    def form_valid(self, form):
        from_email = form.cleaned_data.get("contact_email")
        message = form.cleaned_data.get("more_info")

        help_category = form.cleaned_data.get("help_category")

        send_email(
            settings.ISED_EMAIL_ADDRESS,
            {
                "subject_type": subject.get(help_category),
                "message": message,
                "from_email": from_email,
            },
            settings.ISED_TEMPLATE_ID,
        )
        return super().form_valid(form)


class QRSupportPageView(TemplateView):
    template_name = "register/qr_support_page.html"
