from django import forms


class AutocompleteWidget(forms.widgets.TextInput):
    template_name = "register/includes/autocomplete_input.html"

class PhoneExtensionWidget(forms.widgets.TextInput):
    template_name="register/includes/phone_extension.html"