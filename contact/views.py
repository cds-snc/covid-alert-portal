from django.views.generic import FormView
from django.conf import settings
from django.urls import reverse_lazy
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from .forms import ContactForm


class ContactFormView(FormView):
    template_name = "contact/form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:success")

    def form_valid(self, form):
        try:
            # It's a bit sad, but if we send to freshdesk when running tests (which happens a lot),
            # Freshdesk will spam everyone email about "A new ticket has been created"
            if not settings.TESTING:
                form.send_freshdesk()
        except ValidationError as e:
            form.add_error(NON_FIELD_ERRORS, e.message)
            return self.form_invalid(form)

        return super().form_valid(form)
