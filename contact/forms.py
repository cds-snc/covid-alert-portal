from django import forms
from django.utils.translation import gettext as _
from requests import post


class ContactForm(forms.Form):
    name = forms.CharField(label=_('Your name'))
    email = forms.EmailField(
        label=_('Your email address'),
        error_messages={'required':_("Enter your email address if you want to contact us")}
    )
    feedback = forms.CharField(
        label=_('Ask questions or give feedback'),
        error_messages={'required':_('You need to tell us about your issue before you contact us')},
        widget=forms.Textarea
    )

    def is_valid(self):

        pass
