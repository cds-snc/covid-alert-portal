from register.models import Location
from .models import Notification, SEVERITY
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import transaction
from django.shortcuts import redirect
from django.utils.translation import get_language
from django.views.generic import (
    FormView,
    ListView,
    TemplateView,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from portal.mixins import Is2FAMixin
from .forms import DateForm, SeverityForm
from datetime import datetime
import pytz


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
        if 'num_dates' not in request.session:
            request.session['num_dates'] = 1

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        adjust_dates = request.POST.get('adjust_dates')
        if adjust_dates:
            num_dates = self.request.session['num_dates']
            if adjust_dates == 'add':
                if num_dates < 5:
                    self.request.session['num_dates'] = num_dates + 1
            else:
                if num_dates > 1:
                    self.request.session['num_dates'] = num_dates - 1
                    self.request.session.pop(f'alert_datetime_{num_dates - 1}', None)
            return redirect(reverse_lazy("exposure_notifications:datetime"))
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        # This provides init arguments for the form instance
        kwargs = super().get_form_kwargs()
        kwargs['num_dates'] = self.request.session.get('num_dates', 1)
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['min_date'] = '2021-01-01'  # Start of the year for simplicity
        context['max_date'] = datetime.now().strftime('%Y-%m-%d')  # Set max date to today
        context['language'] = get_language()
        return context

    def get_initial(self):
        # Populate the form with initial session data if we have it
        initial_data = {}
        for i in range(self.request.session.get('num_dates', 1)):
            ts = self.request.session.get(f'alert_datetime_{i}')
            if ts:
                dt = datetime.fromtimestamp(ts)
                initial_data.update({f'year_{i}': dt.year, f'month_{i}': dt.month, f'day_{i}': dt.day})
        return initial_data

    def form_valid(self, form):
        # Cache the datetime list for the next step
        for i in range(self.request.session.get('num_dates', 1)):
            dt = form.cleaned_data.get(f'date_{i}')
            self.request.session[f'alert_datetime_{i}'] = dt.timestamp()
        response = super().form_valid(form)
        return response


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
        context["map_link"] = "https://maps.google.com/?q=" + str(location)

        num_dates = self.request.session.get('num_dates', 1)
        context['num_dates'] = num_dates
        context['dates'] = []
        for i in range(num_dates):
            dt = datetime.fromtimestamp(self.request.session[f'alert_datetime_{i}'])
            context['dates'].append(dt.strftime(DATETIME_FORMAT))
        return context

    @transaction.atomic
    def form_valid(self, form):
        # Use a transaction to commit all or nothing for the notifications
        try:
            with transaction.atomic():
                for i in range(self.request.session.get('num_dates', 1)):
                    self.post_notification(form, i)

                # Continue with the redirect
                response = super().form_valid(form)
                return response

        except KeyError:
            # Post request without having data cached in session
            return redirect(reverse_lazy("outbreaks:search"))
        except IntegrityError:
            # TODO: redirect to page warning of existing entry
            raise

    def post_notification(self, form, i):
        # Ensure that the datetime is aware (might not be if unit testing or something)
        tz = pytz.timezone(settings.TIME_ZONE or "UTC")
        dt = datetime.fromtimestamp(self.request.session[f'alert_datetime_{i}']).replace(
            tzinfo=tz
        )

        # Create the notification
        notification = Notification(
            severity=self.request.session['alert_level'],
            start_date=dt,
            end_date=dt,
            location_id=self.request.session['alert_location'],
            created_by=self.request.user,
        )
        notification.save()


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

        num_dates = self.request.session.pop('num_dates', 1)
        context['num_dates'] = num_dates
        context['dates'] = []
        for i in range(num_dates):
            dt = datetime.fromtimestamp(self.request.session[f'alert_datetime_{i}'])
            context['dates'].append(dt.strftime(DATETIME_FORMAT))

        return context


class HistoryView(PermissionRequiredMixin, Is2FAMixin, ListView):
    permission_required = ["profiles.can_send_alerts"]
    paginate_by = 10
    model = Notification
    template_name = "history.html"

    def get_queryset(self):
        province = self.request.user.province.abbr
        search = self.request.GET.get("search_text")
        if search:
            # 'icontains' will produce a case-insensitive SQL 'LIKE' statement which adds a certain level of 'fuzziness' to the search
            # Fuzzy search either the name or the address field
            # search within the same province as the user or CDS
            if self.request.user.is_superuser:
                return Notification.objects.filter(
                    Q(location__name__icontains=search)
                    | Q(location__address__icontains=search)
                ).order_by("-created_date")
            else:
                return Notification.objects.filter(
                    Q(location__province=province)
                    & Q(
                        Q(location__name__icontains=search)
                        | Q(location__address__icontains=search)
                    )
                ).order_by("-created_date")

        # If we don't have search text then just return all results within this province
        if self.request.user.is_superuser:
            return Notification.objects.all().order_by("-created_date")
        return Notification.objects.filter(location__province=province).order_by(
            "-created_date"
        )


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
