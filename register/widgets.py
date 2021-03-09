from django import forms


class AutocompleteWidget(forms.widgets.TextInput):
    template_name = "register/includes/autocomplete_input.html"
