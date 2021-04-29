from django.contrib import admin
from .models import Notification, NotificationSummary
from django.db.models import Count


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "start_date",
        "end_date",
        "created_date",
        "created_by",
        "severity",
        "location",
        "short_code",
    ]

    list_display_links = None

    def short_code(self, obj):
        return obj.location.short_code

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NotificationSummary)
class NotificationSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/notification_summary_change_list.html"
    date_hierarchy = "created_date"

    class Media:
        css = {"all": ("css/admin.css",)}

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
            qs.values("location__province")
            .annotate(total=Count("location__province"))
            .order_by("-total")
        )
        response.context_data["province_summary"] = list(qs_province)

        response.context_data["province_summary_total"] = dict(
            qs.aggregate(total=Count("location__province"))
        )

        qs_city = (
            qs.values("location__city")
            .annotate(total=Count("location__city"))
            .order_by("-total")
        )

        response.context_data["city_summary"] = list(qs_city)
        response.context_data["city_summary_total"] = dict(
            qs.aggregate(total=Count("location__city"))
        )

        qs_location = (
            qs.values("location__name")
            .annotate(total=Count("location__name"))
            .order_by("-total")
        )

        response.context_data["location_summary"] = list(qs_location)
        response.context_data["location_summary_total"] = dict(
            qs.aggregate(total=Count("location"))
        )

        return response
