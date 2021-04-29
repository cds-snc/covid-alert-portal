from .models import Notification
from django.db.models import Q
from django import forms
from django.utils.translation import get_language, gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from portal.widgets import CDSRadioWidget
from portal.forms import HealthcareBaseForm
from datetime import datetime
from calendar import month_name
import pytz

severity_choices = [
    ("1", _("Self-monitor")),
    ("2", _("Self-isolate")),
    ("3", _("Get tested immediately")),
]
hour_format = "%-H:%M" if get_language() == "fr" else "%-I:%M %p"
start_hours = []
end_hours = []
for hour in range(24):
    display_hour = (
        f"{hour}:00:00:000000",
        datetime.strftime(datetime(2020, 1, 1, hour), hour_format),
    )
    display_hour_30 = (
        f"{hour}:30:00:000000",
        datetime.strftime(datetime(2020, 1, 1, hour, 30), hour_format),
    )
    display_hour_29 = (
        f"{hour}:29:59:999999",
        datetime.strftime(datetime(2020, 1, 1, hour, 29, 59), hour_format),
    )
    display_hour_59 = (
        f"{hour}:59:59:999999",
        datetime.strftime(datetime(2020, 1, 1, hour, 59, 59), hour_format),
    )
    start_hours.append(display_hour)
    start_hours.append(display_hour_30)
    end_hours.append(display_hour_29)
    end_hours.append(display_hour_59)

month_choices = [(i + 1, month_name[i + 1]) for i in range(12)]
month_choices.insert(0, (-1, _("Select")))


class DateForm(HealthcareBaseForm):
    day = forms.IntegerField(
        label=_("Day"), min_value=1, max_value=31, widget=forms.NumberInput
    )
    month = forms.ChoiceField(
        label=_("Month"),
        choices=month_choices,
    )
    year = forms.IntegerField(
        label=_("Year"),
        min_value=2021,
        max_value=datetime.now().year,
        widget=forms.NumberInput,
    )

    def __init__(self, *args, **kwargs):
        show_time_fields = kwargs.pop("show_time_fields", None)
        alert_location = kwargs.pop("alert_location", None)
        super().__init__(*args, **kwargs)

        self.alert_location = alert_location
        if show_time_fields:
            self.fields["start_time"] = forms.ChoiceField(
                label=_("From"),
                choices=start_hours,
            )
            self.fields["end_time"] = forms.ChoiceField(
                label=_("To"),
                choices=end_hours,
            )

    def clean(self):
        # Validate each date provided to ensure that it is in fact a correct date
        cleaned_data = super().clean()
        invalid_date_error_msg = _("Invalid date specified.")

        try:
            start_date = self.get_valid_date(cleaned_data, "start")
            end_date = self.get_valid_date(cleaned_data, "end")
            DateForm.validate_date_entry(self, start_date, end_date, self.alert_location)
        except ValueError:
            self.add_error(None, invalid_date_error_msg)

    @staticmethod
    def validate_date_entry(form, start_date, end_date, alert_location):
        tz = pytz.timezone(settings.PORTAL_LOCAL_TZ or settings.TIME_ZONE or "UTC")
        start_later_end_error_msg = _('"To" must be later than "From".')
        overlap_notification_error_tmpl = _(
            "Someone already notified people who were there between {} and {}."
        )
        if start_date >= end_date:
            form.add_error(None, start_later_end_error_msg)
            raise ValidationError(start_later_end_error_msg)
        notifications = DateForm.get_notification_intersection(
            start_date, end_date, alert_location
        )
        if notifications:
            error_list = []
            for idx, notification in enumerate(notifications):
                error_list.append(
                    ValidationError(
                        overlap_notification_error_tmpl.format(
                            notification.start_date.astimezone(tz).strftime("%c"),
                            notification.end_date.astimezone(tz).strftime("%c"),
                        ),
                        code="warning",
                    )
                )
            form.add_error(None, error_list)

    def get_valid_date(self, data, start_or_end="start"):
        tz = pytz.timezone(
            settings.PORTAL_LOCAL_TZ
        )  # TODO (mvp pilot setting) Change this for multi-tz rollout
        default_time = (
            "0:00:00:000000" if start_or_end == "start" else "23:59:59:999999"
        )
        hour, minute, second, ms = [
            int(x) for x in data.get(f"{start_or_end}_time", default_time).split(":")
        ]
        return tz.localize(
            datetime(
                year=int(data.get("year", -1)),
                month=int(data.get("month", -1)),
                day=int(data.get("day", -1)),
                hour=hour,
                minute=minute,
                second=second,
                microsecond=ms,
            )
        )

    @staticmethod
    def get_notification_intersection(start_date, end_date, location):
        return Notification.objects.filter(
            Q(start_date__range=[start_date, end_date], location__id=location)
            | Q(end_date__range=[start_date, end_date], location__id=location)
        )


class SeverityForm(HealthcareBaseForm):
    alert_level = forms.ChoiceField(
        label="",
        choices=severity_choices,
        widget=CDSRadioWidget(attrs={"class": "multichoice-radio"}),
    )
