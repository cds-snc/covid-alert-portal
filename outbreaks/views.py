from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

from register.models import Location
from .models import Notification, SEVERITY
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models.functions import Lower
from django.db.models import Q
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import FormView, ListView, TemplateView, View
from django.utils.translation import get_language, gettext_lazy as _
from django.contrib.auth.mixins import PermissionRequiredMixin
from portal.mixins import Is2FAMixin
from .forms import end_hours, DateForm, SeverityForm
from .protobufs import outbreak_pb2
from datetime import datetime
import pytz
from .forms import severity_choices
from register.forms import location_choices
import requests
import logging
import re


def get_datetime_format(language):
    if language == "fr":
        return "%Y-%m-%d %-H:%M"
    return "%Y-%m-%d %-I:%M %p"


def get_time_format(language):
    if language == "fr":
        return "%-H:%M"
    return "%-I:%M %p"


def process_query(s):
    """
    Converts the user's search string into something suitable for passing to
    to_tsquery. Supports wildcard/partial strings and assumes AND operator
    For example: "Tim:* & Horton:* & Toronto:*"
    """
    query = re.sub(r"[!\'()|&]", " ", s).strip()

    if query:
        # Append wildcard to each substring
        query = " ".join([s + ":*" for s in query.split()])

        # add AND operator between search terms
        query = re.sub(r"\s+", " & ", query)

    return query


class SearchView(PermissionRequiredMixin, Is2FAMixin, ListView):
    permission_required = ["profiles.can_send_alerts"]
    paginate_by = 5
    model = Location
    template_name = "search.html"

    def get_queryset(self):
        searchStr = self.request.GET.get("search_text")
        if searchStr:
            # Heads-up: this code relies on Postgres full text search
            # features, so will not work with a SQLite database
            #
            # Also note: this was originally based on Django built-in functions,
            # but they don't support partial string search so refactored
            # to use postgres directly, see:
            # https://www.fusionbox.com/blog/detail/partial-word-search-with-postgres-full-text-search-in-django/632/

            query = process_query(searchStr)
            queryset = Location.objects.all()

            queryset = queryset.extra(
                where=[
                    """
                    to_tsvector('english', unaccent(concat_ws(' ',
                        register_location.name,
                        register_location.address,
                        register_location.city,
                        register_location.postal_code
                    ))) @@ to_tsquery('english', unaccent(%s))
                    """
                ],
                params=[query],
            )

            # If you're not a superuser, search only in your province
            if not self.request.user.is_superuser:
                province = self.request.user.province.abbr
                queryset = queryset.filter(province=province)

            return queryset

        return Location.objects.none()


class ProfileView(PermissionRequiredMixin, Is2FAMixin, FormView):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "profile.html"
    form_class = forms.Form
    success_url = reverse_lazy("outbreaks:datetime")

    def get(self, request, *args, **kwargs):
        # purge selected dates to reset wizard flow
        if request.session.get("selected_dates"):
            del request.session["selected_dates"]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            # Fetch the location
            location = Location.objects.get(id=self.kwargs["pk"])
            context["location"] = location
            context["map_link"] = "https://maps.google.com/?q=" + str(location)
            location.category = dict(location_choices)[location.category]
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


class DatetimeView(PermissionRequiredMixin, Is2FAMixin, View):
    permission_required = ["profiles.can_send_alerts"]
    template_name = "datetime.html"

    def get(self, request, *args, **kwargs):
        # Ensure we have a cached location
        if "alert_location" not in request.session:
            return redirect(reverse_lazy("outbreaks:search"))
        idx = kwargs.pop("idx", None)
        if idx is not None:  # time to delete a thing
            request.session["selected_dates"] = [
                dt
                for i, dt in enumerate(request.session.get("selected_dates", []))
                if i != idx
            ]
        form = DateForm()
        next_button_submit_form_ind = not request.session.get("selected_dates")
        next_button_show = True
        show_date_form = not request.session.get("selected_dates")
        return render(
            request,
            self.template_name,
            self.get_context_data(
                form=form,
                show_date_form=show_date_form,
                next_button_show=next_button_show,
                next_button_submit_form_ind=next_button_submit_form_ind,
            ),
        )

    def post(self, request, *args, **kwargs):
        """
        POST scenarios:
        * Add time range -> display date fields
        * Clear time range -> hide date fields and reset to default start / end
        * Add date (save to session) -> validate form and save
        * Show add date -> display date form
        * Unshow add date -> hide date form
        * Remove date
        * Done/Next (no more to save) -> redirect to success
        """
        show_time_fields = False
        show_date_form = True
        show_errors = False
        success_url = reverse_lazy("outbreaks:severity")
        do_post = request.POST.get("do_post", None)
        post_data = request.POST
        next_button_show = not request.session.get("selected_dates")
        next_button_submit_form_ind = not request.session.get("selected_dates")
        form = None
        if not do_post:  # no form to submit, going next
            if not request.session.get("selected_dates"):
                return HttpResponseRedirect(reverse_lazy("outbreaks:datetime"))
            return HttpResponseRedirect(success_url)

        if do_post == "add_date":  # submitting a form
            form = DateForm(
                post_data,
                alert_location=request.session["alert_location"],
                show_time_fields=post_data.get("start_time", None),
            )
            if form.is_valid():
                if self.save_form_dates(form):
                    return HttpResponseRedirect(reverse_lazy("outbreaks:datetime"))
            show_errors = True

        # not submitting a form, other toggles or form invalid
        elif do_post == "cancel":
            return HttpResponseRedirect(reverse_lazy("outbreaks:datetime"))
        elif do_post == "show_date_form":
            show_date_form = True
            post_data = None  # re-init form
        if request.POST.get("start_time", None) or do_post == "add_time":
            show_time_fields = True
            if do_post == "add_time":
                post_data = request.POST.copy()  # make it mutable to init end_time
                post_data.appendlist("end_time", end_hours[-1])
        if do_post == "clear_time":
            show_time_fields = False

        # only re-rendering form if shifting time mode, or failed validation
        form = (
            DateForm(post_data, show_time_fields=show_time_fields) if not form else form
        )
        context = self.get_context_data(
            form=form,
            show_errors=show_errors,  # we're not submitting here
            show_date_form=show_date_form,
            show_time_fields=show_time_fields,
            do_post=do_post,
            next_button_show=next_button_show,
            next_button_submit_form_ind=next_button_submit_form_ind,
        )
        return render(request, self.template_name, context)

    def save_form_dates(self, form):
        """
        Cache the currently entered valid datetime entries before adding/removing new entries so that the
        user hopefully doesn't experience strange jumps in continuity with values changing/disappearing
        """
        selected_dates = self.request.session.get("selected_dates", [])
        start_dt = form.get_valid_date(form.data)
        end_dt = form.get_valid_date(form.data, "end")
        start_ts = start_dt.timestamp()
        end_ts = end_dt.timestamp()
        overlap_notification_error_tmpl = _(
            "A conflicting time range: ({}) was entered below."
        )
        date_entry_tmpl = _("{} from {} to {}")

        for date_entry in selected_dates:  # check local intersection
            selected_start_ts = date_entry["start_ts"]
            selected_end_ts = date_entry["end_ts"]
            # thanks Martin! https://wiki.c2.com/?TestIfDateRangesOverlap
            if start_ts <= selected_end_ts and selected_start_ts <= end_ts:
                form.add_error(
                    None,
                    ValidationError(
                        overlap_notification_error_tmpl.format(
                            date_entry["notification_txt"]
                        ),
                        code="warning",
                    ),
                )
                return False

        start_dmy_fmt = "%e %B %Y"
        start_dmy = start_dt.strftime(start_dmy_fmt)
        start_hm = start_dt.strftime(get_time_format(get_language()))
        end_hm = end_dt.strftime(get_time_format(get_language()))
        notification_txt = date_entry_tmpl.format(start_dmy, start_hm, end_hm)
        date_entry = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "notification_txt": notification_txt,
        }
        selected_dates.append(date_entry)
        self.request.session["selected_dates"] = selected_dates
        return True

    def get_context_data(self, *args, **kwargs):
        # context = super().get_context_data(*args, **kwargs)
        context = {**kwargs}
        context["min_date"] = "2021-01-01"  # Start of the year for simplicity
        context["max_date"] = (
            datetime.utcnow()
            .replace(
                tzinfo=pytz.timezone(settings.PORTAL_LOCAL_TZ)
                # TODO this may need refactoring for client side max date calculation beyond PORTAL_LOCAL_TZ
            )
            .strftime("%Y-%m-%d")
        )  # Set max date to today
        context["language"] = get_language()
        if context.get("show_errors", False):
            context["warning_ind"] = (
                context["form"].non_field_errors().data[0].code == "warning"
            )
        return context


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
        if "alert_location" not in request.session or not request.session.get(
            "selected_dates", None
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
            or not request.session.get("selected_dates", None)
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
        context["dates"] = self.request.session["selected_dates"]
        return context

    def form_valid(self, form):
        # Use a transaction to commit all or nothing for the notifications
        with transaction.atomic():
            notifications = []
            try:
                for date_entry in self.request.session["selected_dates"]:
                    notifications.append(
                        self.post_notification(
                            date_entry,
                            self.request.session["alert_level"],
                            self.request.session["alert_location"],
                            self.request.user,
                        )
                    )
            except KeyError:
                return redirect(reverse_lazy("outbreaks:search"))

            # Post the saved notifications to the server
            for notification in notifications:
                self.notify_server(notification)

            # Continue with the redirect
            response = super().form_valid(form)
            return response

    def post_notification(self, date_entry, severity, location_id, user):
        # Ensure that the datetime is aware (might not be if unit testing or something)
        tz = pytz.timezone(settings.TIME_ZONE or "UTC")
        start_dt = datetime.fromtimestamp(date_entry["start_ts"]).replace(tzinfo=tz)
        end_dt = datetime.fromtimestamp(date_entry["end_ts"]).replace(tzinfo=tz)

        # Create the notification
        notification = Notification(
            severity=severity,
            start_date=start_dt,
            end_date=end_dt,
            location_id=location_id,
            created_by=user,
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
            or not request.session.get("selected_dates", None)
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
        context["dates"] = self.request.session["selected_dates"]
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
            # 'icontains' will produce a case-insensitive SQL 'LIKE' statement which adds a certain level of
            # 'fuzziness' to the search
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
