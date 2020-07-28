from django.views.generic import FormView
from django.urls import reverse_lazy

from .forms import ContactForm


class ContactFormView(FormView):
    template_name = 'contact/form.html'
    form_class = ContactForm
    success_url = reverse_lazy("contact:success")
