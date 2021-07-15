from datetime import timedelta
from functools import partial
from urllib.parse import urlencode

from django.contrib import admin, messages
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from portal.mixins import ExportCsvMixin
from .forms import send_email
from .models import Registrant, Location, LocationSummary, Survey, RegistrantSurvey

SURVEY_FILTER_DAY_DIFF = 14


class LocationInline(admin.TabularInline):
    model = Location
    readonly_fields = [
        "short_code",
        "name",
        "category",
        "address",
        "city",
        "province",
        "postal_code",
    ]
    exclude = [
        "address_2",
        "category_description",
        "postal_code",
        "contact_name",
        "contact_phone",
        "contact_phone_ext",
        "contact_email",
    ]
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class SurveySentFilter(admin.SimpleListFilter):
    title = _("Surveys Completed")
    parameter_name = "surveys"

    def lookups(self, request, model_admin):
        result = []
        surveys = Survey.objects.all()
        if surveys:
            result.append(("none", "None sent"))
            for survey in surveys:
                result.append((f"{survey.id}:0", f"{survey.title}: None"))
                result.append((f"{survey.id}:1", f"{survey.title}: Sent"))
            result.append(("all", "All surveys sent"))
        return result

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.exclude(registrantsurvey__registrant__in=queryset)
        elif self.value() == "all":
            surveys = Survey.objects.all()
            for survey in surveys:
                queryset = queryset.filter(
                    registrantsurvey__registrant__in=queryset,
                    registrantsurvey__survey=survey,
                )
            return queryset.distinct()
        elif self.value():
            id, code = self.value().split(":")
            if code == "0":
                return queryset.exclude(registrantsurvey__survey_id=id)
            elif code == "1":
                return queryset.filter(registrantsurvey__survey_id=id).distinct()


class SurveyTimeSinceFilter(admin.SimpleListFilter):
    title = _(f"{SURVEY_FILTER_DAY_DIFF} days since survey sent")
    parameter_name = "timesince"

    def lookups(self, request, model_admin):
        result = []
        date_offset = timezone.now() - timedelta(days=SURVEY_FILTER_DAY_DIFF)
        offset_sent_surveys = RegistrantSurvey.objects.filter(
            sent_ts__lte=date_offset
        ).distinct("survey")
        for reg_survey in offset_sent_surveys:
            result.append(
                (
                    f"{reg_survey.survey.id}:offset",
                    f"{reg_survey.survey.title}: {SURVEY_FILTER_DAY_DIFF}+ days",
                )
            )
        return result

    def queryset(self, request, queryset):
        if self.value():
            id, code = self.value().split(":")
            if code == "offset":
                date_offset = timezone.now() - timedelta(days=SURVEY_FILTER_DAY_DIFF)
                return queryset.filter(
                    registrantsurvey__survey_id=id,
                    registrantsurvey__sent_ts__lte=date_offset,
                )


class CreatedPosterFilter(admin.SimpleListFilter):
    title = _("Created a Poster")
    parameter_name = "poster"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"), ("no", "No"))

    def queryset(self, request, queryset):
        if self.value():
            created = self.value() == "yes"
            return queryset.filter(location__isnull=not created).distinct()


@admin.register(Registrant)
class RegistrantAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ["email", "surveys", "province", "created_poster", "created", "id"]
    list_filter = (
        CreatedPosterFilter,
        SurveySentFilter,
        SurveyTimeSinceFilter,
        "location__province",
        "location__city",
    )
    inlines = [
        LocationInline,
    ]
    search_fields = ["id", "email", "location__city", "location__province"]
    actions = ["export_as_csv"]

    def province(self, obj):
        locations = obj.location_set.all()
        if locations:
            return locations[0].province if len(locations) == 1 else "Multiple"
        return ""

    def surveys(self, obj):
        surveys = Survey.objects.all()
        val = ""
        count = 0
        for survey in surveys:
            delimiter = "" if count == 0 else ", "
            registrant_surveys = RegistrantSurvey.objects.filter(
                registrant=obj, survey=survey
            )
            if registrant_surveys:
                count += 1
                val += f"{delimiter}{survey}"
        return val

    def get_actions(self, request):
        actions = super().get_actions(request)
        surveys = Survey.objects.all()
        for survery in surveys:
            sender_func = partial(self.send_survey_by_id, survery.id)
            actions[f"survey_{survery.id}"] = (
                sender_func,
                f"survey_{survery.id}",
                f"Immediately email {survery} to registrant(s)",
            )
        return actions

    @staticmethod
    def send_survey_by_id(id, modeladmin, request, queryset):
        count = 0
        for registrant in queryset:
            if not registrant.location_set.exists():
                modeladmin.message_user(
                    request,
                    _(f"{registrant.email} has not created a poster."),
                    messages.WARNING,
                )
            else:
                reg_surveys = registrant.registrantsurvey_set.filter(survey_id=id)
                if reg_surveys:
                    modeladmin.message_user(
                        request,
                        _(
                            f"{registrant.email} has already had this survey sent to them."
                        ),
                        messages.WARNING,
                    )
                else:
                    reg_survey = RegistrantSurvey.objects.create(
                        registrant=registrant,
                        survey_id=id,
                        sent_by=request.user,
                        sent_ts=timezone.now(),
                    )
                    try:
                        survey = reg_survey.survey
                        template_id = (
                            survey.en_notify_template_id
                            if registrant.language_cd == "en"
                            else survey.fr_notify_template_id
                        )
                        query_param_dict = (
                            {survey.registrant_id_url_param: str(registrant.id)}
                            if survey.append_registrant_id_ind
                            else {}
                        )
                        if survey.append_venue_tag_ind:
                            query_param_dict.update(
                                {
                                    survey.venue_tag_url_param: ",".join(
                                        [
                                            location["category"]
                                            for location in registrant.location_set.all()
                                            .distinct("category")
                                            .values("category")
                                        ]
                                    )
                                }
                            )
                        if query_param_dict:
                            full_url = f"{survey.url}?{urlencode(query_param_dict)}"
                        else:
                            full_url = survey.url
                        send_email(
                            registrant.email,
                            {"url": full_url},
                            template_id,
                        )
                        count += 1
                    except Exception as e:
                        modeladmin.message_user(
                            request,
                            _(f"{str(e)} :: email: {registrant.email}"),
                            messages.ERROR,
                        )
                        reg_survey.delete()
        if count:
            modeladmin.message_user(
                request, _(f"Sent {count} messages successfully"), messages.SUCCESS
            )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin, ExportCsvMixin):
    date_hierarchy = "created"
    list_display = [
        "name",
        "city",
        "province",
        "short_code",
        "registrant_id",
        "registrant_email",
    ]
    list_filter = (
        "province",
        "city",
    )
    actions = ["export_as_csv"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LocationSummary)
class LocationSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/location_summary_change_list.html"
    date_hierarchy = "created"

    class Media:
        css = {"all": ("css/admin.css",)}

    def has_add_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        qs_province = (
            qs.values("province").annotate(total=Count("province")).order_by("-total")
        )
        response.context_data["province_summary"] = list(qs_province)

        response.context_data["province_summary_total"] = dict(
            qs.aggregate(total=Count("province"))
        )

        qs_city = qs.values("city").annotate(total=Count("city")).order_by("-total")

        response.context_data["city_summary"] = list(qs_city)
        response.context_data["city_summary_total"] = dict(
            qs.aggregate(total=Count("city"))
        )

        return response
