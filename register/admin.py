from django.contrib import admin

from .models import Registrant, Location, LocationSummary
from django.db.models import Count


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


@admin.register(Registrant)
class RegistrantAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "created"]
    inlines = [
        LocationInline,
    ]
    search_fields = ["id", "email"]

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ["name", "city", "province", "short_code", "registrant"]
    list_filter = (
        "province",
        "city",
    )

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
