from django.views.generic import FormView
from django.urls import reverse_lazy
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from .forms import ContactForm


class ContactFormView(FormView):
    template_name = "contact/form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:success")

    def form_valid(self, form):
        try:
            form.send_freshdesk()
        except ValidationError as e:
            form.add_error(NON_FIELD_ERRORS, e.message)
            return self.form_invalid(form)

        return super().form_valid(form)
