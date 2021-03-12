from django import forms
from django.utils.translation import get_language, gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from portal.widgets import CDSRadioWidget
from portal.forms import HealthcareBaseForm
from datetime import datetime
import pytz

severity_choices = [
    ("1", _("Self-monitor")),
    ("2", _("Self-isolate")),
    ("3", _("Get tested immediately")),
]


class DateForm(HealthcareBaseForm):
    def __init__(self, num_dates=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_dates = num_dates

        hour_format = "%-H:%M" if get_language() == "fr" else "%-I:%M %p"
        hours = [
            (str(hour), datetime.strftime(datetime(2020, 1, 1, hour), hour_format))
            for hour in range(24)
        ]
        hours.append(
            ("24", datetime.strftime(datetime(2020, 1, 1, 23, 59), hour_format))
        )

        # Generate the desired number of date fields
        for i in range(num_dates):
            self.fields[f"day_{i}"] = forms.IntegerField(
                label=_("Day"), min_value=1, max_value=31, widget=forms.TextInput
            )
            self.fields[f"month_{i}"] = forms.IntegerField(
                label=_("Month"),
                min_value=1,
                max_value=12,
                widget=forms.TextInput,
            )
            self.fields[f"year_{i}"] = forms.IntegerField(
                label=_("Year"),
                min_value=2021,
                max_value=datetime.now().year,
                initial=2021,
                widget=forms.TextInput,
            )
            self.fields[f"start_hour_{i}"] = forms.ChoiceField(
                label=_("From"),
                choices=hours[:-1],
                initial=hours[0],
            )
            self.fields[f"end_hour_{i}"] = forms.ChoiceField(
                label=_("To"),
                choices=hours[1:],
                initial=hours[-1],
            )
        # Add the fieldset to the meta class
        # Idea adapted from: https://schinckel.net/2013/06/14/django-fieldsets/
        meta = getattr(self, "Meta", None)
        meta.fieldsets = tuple(
            (
                f"date_{i}",
                {
                    "fields": (
                        f"day_{i}",
                        f"month_{i}",
                        f"year_{i}",
                        f"start_hour_{i}",
                        f"end_hour_{i}",
                    )
                },
            )
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
                cleaned_data[f"start_date_{i}"] = self.get_valid_date(
                    cleaned_data, i, "start"
                )
                cleaned_data[f"end_date_{i}"] = self.get_valid_date(
                    cleaned_data, i, "end"
                )
            except ValueError:
                is_valid = False
                meta = getattr(self, "Meta", None)
                meta.fieldsets[i][1]["error"] = error_msg

        if not is_valid:
            raise ValidationError(error_msg)

    def get_valid_date(self, data, i, start_or_end="start"):
        tz = pytz.timezone(settings.TIME_ZONE or "UTC")
        hour = int(data.get(f"{start_or_end}_hour_{i}", -1))
        return datetime(
            year=int(data.get(f"year_{i}", -1)),
            month=int(data.get(f"month_{i}", -1)),
            day=int(data.get(f"day_{i}", -1)),
            hour=hour if hour != 24 else 23,
            minute=0 if hour != 24 else 59,
            second=0 if hour != 24 else 59,
        ).replace(tzinfo=tz)

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
