from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from waffle.mixins import WaffleSwitchMixin


from .models import Registrant
from .forms import EmailForm, RegistrantNameForm


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
    success_url = reverse_lazy("register:confirmation")
    template_name = "register/registrant_name.html"


class RegisterStartPageView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/start.html"


class RegisterConfirmationPageView(WaffleSwitchMixin, TemplateView):
    waffle_switch = "QR_CODES"
    template_name = "register/confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registrant_email"] = self.request.session.get("registrant_email")
        return context
