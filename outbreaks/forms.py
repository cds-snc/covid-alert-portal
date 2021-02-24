from django import forms
from django.utils.translation import gettext_lazy as _
from portal.widgets import CDSRadioWidget


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : as label suffix

    search_text = forms.CharField(
        max_length=100, label=_("Search for place name or address")
    )


class DateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : as label suffix

    day = forms.IntegerField(label=_("Day"), required=True, min_value=1, max_value=31)
    month = forms.IntegerField(
        label=_("Month"), required=True, min_value=1, max_value=12
    )
    year = forms.IntegerField(
        label=_("Year"), required=True, min_value=2021, max_value=2021, initial=2021
    )


class SeverityForm(forms.Form):
    alert_level = forms.ChoiceField(
        label="",
        choices=[
            ("1", _("Somebody sneezed...")),
            ("2", _("Sirens and lights flashing everywhere!")),
            ("3", _("Zombie apocalypse!!!!")),
        ],
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
