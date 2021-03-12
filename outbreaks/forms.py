from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from portal.widgets import CDSRadioWidget
from portal.forms import HealthcareBaseForm
from datetime import datetime
import pytz
from dateutil import tz

severity_choices = [
    ("1", _("Self-monitor")),
    ("2", _("Self-isolate")),
    ("3", _("Get tested immediately")),
]


class DateForm(HealthcareBaseForm):
    def __init__(self, num_dates=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_dates = num_dates

        # Generate the desired number of date fields
        for i in range(num_dates):
            self.fields[f"day_{i}"] = forms.IntegerField(
                label=_("Day"), min_value=1, max_value=31, widget=forms.TextInput
            )
            self.fields[f"month_{i}"] = forms.IntegerField(
                label=_("Month"),
                min_value=1,
                max_value=datetime.now().month,
                widget=forms.TextInput,
            )
            self.fields[f"year_{i}"] = forms.IntegerField(
                label=_("Year"),
                min_value=2021,
                max_value=2021,
                initial=2021,
                widget=forms.TextInput,
            )

        # Add the fieldset to the meta class
        # Idea adapted from: https://schinckel.net/2013/06/14/django-fieldsets/
        meta = getattr(self, "Meta", None)
        meta.fieldsets = tuple(
            (f"date_{i}", {"fields": (f"day_{i}", f"month_{i}", f"year_{i}")})
            for i in range(num_dates)
        )

    class Meta:
        fieldsets = ()

    def clean(self):
        # Validate each date provided to ensure that it is in fact a correct date
        cleaned_data = super().clean()
        is_valid = True
        error_msg = _("Invalid date specified.")
        for i in range(self.num_dates):
            try:
                cleaned_data[f"date_{i}"] = self.get_valid_date(cleaned_data, i)
            except ValueError:
                is_valid = False
                meta = getattr(self, "Meta", None)
                meta.fieldsets[i][1]["error"] = error_msg

        if not is_valid:
            raise ValidationError(error_msg)

    def get_valid_date(self, data, i, tz_offset_s=0):
        tz_local = tz.tzoffset("NA", tz_offset_s)
        return datetime(
            year=int(data.get(f"year_{i}", -1)),
            month=int(data.get(f"month_{i}", -1)),
            day=int(data.get(f"day_{i}", -1)),
        ).replace(tzinfo=tz_local)

    def add_duplicate_error(self, index):
        error_msg = _(
            "Someone already notified people who were there at this date and time."
        )
        meta = getattr(self, "Meta", None)
        meta.fieldsets[index][1]["error"] = error_msg
        self.add_error(None, error_msg)  # Add a non-field error to flag this state


class SeverityForm(HealthcareBaseForm):
    alert_level = forms.ChoiceField(
        label="",
        choices=severity_choices,
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
