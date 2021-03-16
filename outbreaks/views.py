from register.models import Location
from .models import Notification, SEVERITY
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models.functions import Lower
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.views.generic import (
    FormView,
    ListView,
    TemplateView,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from portal.mixins import Is2FAMixin
from .forms import DateForm, SeverityForm
from .protobufs import outbreak_pb2
from datetime import datetime, timedelta
import pytz
from .forms import severity_choices
from register.forms import location_choices
import requests
import logging


DATETIME_FORMAT = "%Y-%m-%d"


class SearchView(PermissionRequiredMixin, Is2FAMixin, ListView):
    permission_required = ["profiles.can_send_alerts"]
    paginate_by = 5
    model = Location
    template_name = "search.html"

    def get_queryset(self):
        search = self.request.GET.get("search_text")
        if search:
            # 'icontains' will produce a case-insensitive SQL 'LIKE' statement which adds a certain level of 'fuzziness' to the search
            # Fuzzy search either the name or the address field
            # search within the same province as the user or CDS
            province = self.request.user.province.abbr

            if self.request.user.is_superuser:
                return Location.objects.filter(
                    Q(name__icontains=search) | Q(address__icontains=search)
                ).order_by("name")
            else:
                return Location.objects.filter(
                    Q(province=province)
                    & Q(Q(name__icontains=search) | Q(address__icontains=search))
                ).order_by("name")
        return Location.objects.none()


class ProfileView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "profile.html"
    form_class = forms.Form
    success_url = reverse_lazy("outbreaks:datetime")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            # Fetch the location
            location = Location.objects.get(id=self.kwargs["pk"])
            context["location"] = location
            context["map_link"] = "https://maps.google.com/?q=" + str(location)

            # Cache the location for the next steps
            self.request.session["alert_location"] = self.kwargs["pk"].hex

            # Fetch the notification count
            context["num_notifications"] = Notification.objects.filter(
                location=location
            ).count()

        except Location.DoesNotExist:
            # Remove the location cache if users are trying invalid PKs
            del self.request.session["alert_location"]

        return context


class DatetimeView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "datetime.html"
    form_class = DateForm
    success_url = reverse_lazy("outbreaks:severity")

    def get(self, request, *args, **kwargs):
        # Ensure we have a cached location
        if "alert_location" not in request.session:
            return redirect(reverse_lazy("outbreaks:search"))

        # Ensure that we set the initial number of dates
        if "num_dates" not in request.session:
            request.session["num_dates"] = 1

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.save_form_dates()
        adjust_dates = request.POST.get("adjust_dates")
        if adjust_dates:
            num_dates = self.request.session.get("num_dates", 1)
            if adjust_dates == "add" and self.get_form().is_valid():
                # Only add a new date if the current ones are all valid
                if num_dates < 5:
                    num_dates += 1
                    self.request.session["num_dates"] = num_dates
                return redirect(
                    reverse_lazy("outbreaks:datetime") + f"?num_dates={num_dates}"
                )
            elif adjust_dates == "remove":
                # Remove the last date even if there are some errors
                if num_dates > 1:
                    num_dates -= 1
                    self.request.session["num_dates"] = num_dates
                    self.request.session.pop(f"alert_datetime_{num_dates}", None)
                return redirect(
                    reverse_lazy("outbreaks:datetime") + f"?num_dates={num_dates}"
                )

        # Proceed to success or form error
        return response

    def save_form_dates(self):
        """
        Cache the currently entered valid datetime entries before adding/removing new entries so that the
        user hopefully doesn't experience strange jumps in continuity with values changing/disappearing
        """
        form = self.get_form()
        for i in range(self.request.session.get("num_dates", 1)):
            try:
                dt = form.get_valid_date(form.data, i)
                self.request.session[f"alert_datetime_{i}"] = dt.timestamp()
            except ValueError:
                # Don't cache invalid dates
                pass

    def get_form_kwargs(self):
        # This provides init arguments for the form instance
        kwargs = super().get_form_kwargs()
        kwargs["num_dates"] = self.request.session.get("num_dates", 1)
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["min_date"] = "2021-01-01"  # Start of the year for simplicity
        context["max_date"] = datetime.now().strftime(
            "%Y-%m-%d"
        )  # Set max date to today
        context["language"] = get_language()

        """
        A little bit of trickery going on here. If we have 'num_dates' as a query parameter
        then we'll set the focus on the day element of the last date in the form. This is here
        to create a smoother experience in terms of accessibility. When a user using
        voice-over adds or removes a date, the focus should be returned on this newly added element
        """
        num_dates = self.request.GET.get("num_dates")
        if num_dates:
            i = int(num_dates) - 1
            try:
                context["form"].fields[f"day_{i}"].widget.attrs.update(
                    {"autofocus": "autofocus"}
                )
            except KeyError:
                # Only legit numbers should work otherwise ignore it
                pass
        return context

    def get_initial(self):
        # Populate the form with initial session data if we have it
        initial_data = {}
        for i in range(self.request.session.get("num_dates", 1)):
            ts = self.request.session.get(f"alert_datetime_{i}")
            if ts:
                dt = datetime.fromtimestamp(ts)
                initial_data.update(
                    {f"year_{i}": dt.year, f"month_{i}": dt.month, f"day_{i}": dt.day}
                )
        return initial_data

    def form_valid(self, form):
        location = self.request.session["alert_location"]
        for i in range(self.request.session.get("num_dates", 1)):
            dt = form.cleaned_data.get(f"date_{i}")

            # Ensure that the date doesn't exist already for this location
            if self.notification_exists(dt, location):
                form.add_duplicate_error(i)
                return self.form_invalid(form)

            # Cache the datetime list for the next step.
            self.request.session[f"alert_datetime_{i}"] = dt.timestamp()

        return super().form_valid(form)

    def notification_exists(self, dt, location):
        try:
            Notification.objects.get(start_date=dt, location__id=location)
            return True
        except Notification.DoesNotExist:
            return False


class SeverityView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "severity.html"
    form_class = SeverityForm
    success_url = reverse_lazy("outbreaks:confirm")

    def get_initial(self):
        # Populate the form with initial session data if we have it
        return {"alert_level": self.request.session.get("alert_level")}

    def get(self, request, *args, **kwargs):
        # Ensure we have a cached location and datetime
        if (
            "alert_location" not in request.session
            or "alert_datetime_0" not in request.session
        ):
            return redirect(reverse_lazy("outbreaks:search"))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # Cache the level for the next step
        self.request.session["alert_level"] = form.cleaned_data.get("alert_level")
        response = super().form_valid(form)
        return response


class ConfirmView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "confirm.html"
    form_class = forms.Form
    success_url = reverse_lazy("outbreaks:confirmed")

    def get(self, request, *args, **kwargs):
        # Ensure we have all necessary data cached
        if (
            "alert_location" not in request.session
            or "alert_datetime_0" not in request.session
            or "alert_level" not in request.session
        ):
            return redirect(reverse_lazy("outbreaks:search"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # At this point the location PK should be valid so we don't catch the not found exception
        location = Location.objects.get(id=self.request.session["alert_location"])
        context["location"] = location
        context["location_category"] = dict(location_choices)[location.category]
        context["map_link"] = "https://maps.google.com/?q=" + str(location)
        context["alert_level"] = dict(severity_choices)[
            self.request.session["alert_level"]
        ]
        num_dates = self.request.session.get("num_dates", 1)
        context["num_dates"] = num_dates
        context["dates"] = []
        for i in range(num_dates):
            dt = datetime.fromtimestamp(self.request.session[f"alert_datetime_{i}"])
            context["dates"].append(dt.strftime(DATETIME_FORMAT))
        return context

    @transaction.atomic
    def form_valid(self, form):
        # Use a transaction to commit all or nothing for the notifications
        try:
            with transaction.atomic():
                notifications = []
                for i in range(self.request.session.get("num_dates", 1)):
                    notifications.append(self.post_notification(form, i))

                # Post the saved notifications to the server
                for notification in notifications:
                    self.notify_server(notification)

                # Continue with the redirect
                response = super().form_valid(form)
                return response

        except KeyError:
            # Post request without having data cached in session
            return redirect(reverse_lazy("outbreaks:search"))
        except IntegrityError:
            # The duplicate validation is in the datetime view so this
            # should theoretically never happen
            raise

    def post_notification(self, form, i):
        # Ensure that the datetime is aware (might not be if unit testing or something)
        tz = pytz.timezone(settings.TIME_ZONE or "UTC")
        dt = datetime.fromtimestamp(
            self.request.session[f"alert_datetime_{i}"]
        ).replace(tzinfo=tz)

        # Create the notification
        notification = Notification(
            severity=self.request.session["alert_level"],
            start_date=dt,
            # server expects valid interval, give the end of current day
            end_date=dt.replace(hour=23, minute=59, second=59, microsecond=0),
            location_id=self.request.session["alert_location"],
            created_by=self.request.user,
        )
        notification.save()
        return notification

    def notify_server(self, notification):
        token = self.request.user.api_key
        if token:
            try:
                url = settings.API_ENDPOINT.rsplit("/", 1)[0] + "/qr/new-event"
                r = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/protobuf",
                    },
                    data=self.notification_to_pb(notification).SerializeToString(),
                )

                # If we don't get a valid response, throw an exception
                r.raise_for_status()

            except requests.exceptions.HTTPError as err:
                pb_response = outbreak_pb2.OutbreakEventResponse()
                pb_response.ParseFromString(r.content)
                logging.exception(
                    f"Received response code {r.status_code} with {pb_response}."
                )
                logging.exception(
                    f"Unable to notify server of outbreak id: {notification.id}"
                )
                raise err
            except requests.exceptions.RequestException as err:
                logging.exception(f"Something went wrong {err}")
                logging.exception(
                    f"Unable to notify server of outbreak id: {notification.id}"
                )
                raise err

    def notification_to_pb(self, notification):
        pb = outbreak_pb2.OutbreakEvent()
        pb.location_id = notification.location.short_code
        pb.start_time.FromDatetime(notification.start_date)
        pb.end_time.FromDatetime(notification.end_date)
        pb.severity = int(notification.severity)
        return pb


class ConfirmedView(PermissionRequiredMixin, Is2FAMixin, TemplateView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "confirmed.html"

    def get(self, request, *args, **kwargs):
        # Ensure we have all necessary data cached
        if (
            "alert_location" not in request.session
            or "alert_datetime_0" not in request.session
            or "alert_level" not in request.session
        ):
            return redirect(reverse_lazy("outbreaks:search"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        # Fetch and clear the session data for this notification
        location = Location.objects.get(id=self.request.session.pop("alert_location"))
        context = super().get_context_data(*args, **kwargs)
        context["severity"] = self.request.session.pop("alert_level")
        context["location"] = location

        num_dates = self.request.session.pop("num_dates", 1)
        context["num_dates"] = num_dates
        context["dates"] = []
        for i in range(num_dates):
            dt = datetime.fromtimestamp(self.request.session.pop(f"alert_datetime_{i}"))
            context["dates"].append(dt.strftime(DATETIME_FORMAT))

        return context


class HistoryView(PermissionRequiredMixin, Is2FAMixin, ListView):
    permission_required = ["profiles.can_send_alerts"]
    paginate_by = 10
    model = Notification
    template_name = "history.html"
    sort_options = ["name", "address", "date"]

    def get(self, request, *args, **kwargs):
        # Ensure there is a clean sort and order column
        sort = self.request.GET.get("sort")
        order = self.request.GET.get("order")
        search = self.request.GET.get("search_text")
        if not sort or sort not in self.sort_options or order not in ["asc", "desc"]:
            pstr = "?sort=name&order=asc"
            params = f"{pstr}&search_text={search}" if search else pstr
            return redirect(reverse_lazy("outbreaks:history") + params)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        # send the sort and order info to the template
        context = super().get_context_data(*args, **kwargs)
        context["sort"] = self.request.GET.get("sort")
        context["order"] = self.request.GET.get("order")
        return context

    def get_queryset(self):
        province = self.request.user.province.abbr
        search = self.request.GET.get("search_text")
        if search:
            # 'icontains' will produce a case-insensitive SQL 'LIKE' statement which adds a certain level of 'fuzziness' to the search
            # Fuzzy search either the name or the address field
            # search within the same province as the user or CDS
            if self.request.user.is_superuser:
                qs = Notification.objects.filter(
                    Q(location__name__icontains=search)
                    | Q(location__address__icontains=search)
                )
            else:
                qs = Notification.objects.filter(
                    Q(location__province=province)
                    & Q(
                        Q(location__name__icontains=search)
                        | Q(location__address__icontains=search)
                    )
                )
        else:
            # If we don't have search text then just return all results within this province
            if self.request.user.is_superuser:
                qs = Notification.objects.all()
            else:
                qs = Notification.objects.filter(location__province=province)

        # Order the queryset
        return self._order_queryset(qs)

    def _order_queryset(self, qs):
        order = self.request.GET.get("order")
        sort = self.request.GET.get("sort")
        if sort == "name":
            col = Lower("location__name")
            return qs.order_by(col if order == "asc" else col.desc())
        elif sort == "address":
            col = Lower("location__address")
            return qs.order_by(col if order == "asc" else col.desc())
        else:
            col = "start_date"
            return qs.order_by(col if order == "asc" else f"-{col}")


class ExposureDetailsView(PermissionRequiredMixin, Is2FAMixin, TemplateView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "details.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            notification = Notification.objects.get(id=self.kwargs["pk"])
            notification.severity = dict(SEVERITY)[notification.severity]
            context["notification"] = notification
            context["location"] = notification.location
            context["map_link"] = "https://maps.google.com/?q=" + str(
                notification.location
            )
        except Location.DoesNotExist:
            pass
        return context
