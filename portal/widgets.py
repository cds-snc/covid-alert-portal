from django import forms


class CDSRadioWidget(forms.widgets.RadioSelect):
    template_name = "includes/radio_select.html"
