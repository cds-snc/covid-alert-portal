from django.shortcuts import render
from register.models import Location
from .models import Notification, SEVERITY
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import (
    FormView,
    ListView,
    TemplateView,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from portal.mixins import Is2FAMixin
from .forms import SearchForm, DateForm, SeverityForm
from datetime import datetime
import pytz


DATETIME_FORMAT = "%d/%m/%Y"


class StartView(PermissionRequiredMixin, Is2FAMixin, ListView, FormView):
    permission_required = ["profiles.can_send_alerts"]
    paginate_by = 5
    model = Location
    form_class = SearchForm
    template_name = "search.html"

    def get_success_url(self):
        """
        POST request (user submitted search) will populate the search_text query parameter for the subsequent forward to the same page as a GET request
        """
        return "{}?search_text={}".format(
            reverse_lazy("exposure_notifications:start"),
            self.request.POST.get("search_text"),
        )

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
                ).order_by('name')
            else:
                return Location.objects.filter(
                    Q(province=province)
                    & Q(Q(name__icontains=search) | Q(address__icontains=search))
                ).order_by('name')
        return Location.objects.none()


class ProfileView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "profile.html"
    form_class = forms.Form
    success_url = reverse_lazy("exposure_notifications:datetime")

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
    success_url = reverse_lazy("exposure_notifications:severity")

    def get(self, request, *args, **kwargs):
        # Ensure we have a cached location
        if "alert_location" not in request.session:
            return redirect(reverse_lazy("exposure_notifications:start"))
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        # Populate the form with initial session data if we have it
        ts = self.request.session.get("alert_datetime")
        if ts:
            dt = datetime.fromtimestamp(ts)
            return {"year": dt.year, "month": dt.month, "day": dt.day}

    def form_valid(self, form):
        # Cache the datetime list for the next step
        dt = datetime(
            form.cleaned_data.get("year"),
            form.cleaned_data.get("month"),
            form.cleaned_data.get("day"),
        )
        self.request.session["alert_datetime"] = dt.timestamp()
        response = super().form_valid(form)
        return response


class SeverityView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "severity.html"
    form_class = SeverityForm
    success_url = reverse_lazy("exposure_notifications:confirm")

    def get_initial(self):
        # Populate the form with initial session data if we have it
        return {"alert_level": self.request.session.get("alert_level")}

    def get(self, request, *args, **kwargs):
        # Ensure we have a cached location and datetime
        if (
            "alert_location" not in request.session
            or "alert_datetime" not in request.session
        ):
            return redirect(reverse_lazy("exposure_notifications:start"))
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
    success_url = reverse_lazy("exposure_notifications:confirmed")

    def get(self, request, *args, **kwargs):
        # Ensure we have all necessary data cached
        if (
            "alert_location" not in request.session
            or "alert_datetime" not in request.session
            or "alert_level" not in request.session
        ):
            return redirect(reverse_lazy("exposure_notifications:start"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # At this point the location PK should be valid so we don't catch the not found exception
        location = Location.objects.get(id=self.request.session["alert_location"])
        context["location"] = location
        context["map_link"] = "https://maps.google.com/?q=" + str(location)

        dt = datetime.fromtimestamp(self.request.session["alert_datetime"])
        context["alert_datetime"] = dt.strftime(DATETIME_FORMAT)
        return context

    def form_valid(self, form):
        try:
            # Ensure that the datetime is aware (might not be if unit testing or something)
            tz = pytz.timezone(settings.TIME_ZONE or 'UTC')
            dt = datetime.fromtimestamp(self.request.session["alert_datetime"]).replace(tzinfo=tz)

            # Create the notification
            notification = Notification(
                severity=self.request.session["alert_level"],
                start_date=dt,
                end_date=dt,
                location_id=self.request.session["alert_location"],
                created_by=self.request.user,
            )
            notification.save()

            # Continue with the redirect
            response = super().form_valid(form)
            return response

        except KeyError:
            # Post request without having data cached in session
            return redirect(reverse_lazy("exposure_notifications:start"))


class ConfirmedView(PermissionRequiredMixin, Is2FAMixin, TemplateView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "confirmed.html"

    def get(self, request, *args, **kwargs):
        # Ensure we have all necessary data cached
        if (
            "alert_location" not in request.session
            or "alert_datetime" not in request.session
            or "alert_level" not in request.session
        ):
            return redirect(reverse_lazy("exposure_notifications:start"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        # Fetch and clear the session data for this notification
        dt = datetime.fromtimestamp(self.request.session.pop("alert_datetime"))
        str_dt = dt.strftime(DATETIME_FORMAT)
        location = Location.objects.get(id=self.request.session.pop("alert_location"))
        context = super().get_context_data(*args, **kwargs)
        context["severity"] = self.request.session.pop("alert_level")
        context["start_date"] = str_dt
        context["end_date"] = str_dt
        context["location"] = location
        return context


class HistoryView(PermissionRequiredMixin, Is2FAMixin, ListView, FormView):
    permission_required = ["profiles.can_send_alerts"]
    paginate_by = 10
    model = Notification
    form_class = SearchForm
    template_name = "history.html"

    def get_success_url(self):
        """
        POST request (user submitted search) will populate the search_text query parameter for the subsequent forward to the same page as a GET request
        """
        return "{}?search_text={}".format(
            reverse_lazy("exposure_notifications:history"),
            self.request.POST.get("search_text"),
        )

    def get_queryset(self):
        province = self.request.user.province.abbr
        search = self.request.GET.get("search_text")
        if search:
            # 'icontains' will produce a case-insensitive SQL 'LIKE' statement which adds a certain level of 'fuzziness' to the search
            # Fuzzy search either the name or the address field
            # search within the same province as the user or CDS
            if self.request.user.is_superuser:
                return Notification.objects.filter(
                    Q(location__name__icontains=search) | Q(location__address__icontains=search)
                ).order_by('-created_date')
            else:
                return Notification.objects.filter(
                    Q(location__province=province)
                    & Q(
                        Q(location__name__icontains=search)
                        | Q(location__address__icontains=search)
                    )
                ).order_by('-created_date')

        # If we don't have search text then just return all results within this province
        if self.request.user.is_superuser:
            return Notification.objects.all().order_by('-created_date')
        return Notification.objects.filter(location__province=province).order_by('-created_date')


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
