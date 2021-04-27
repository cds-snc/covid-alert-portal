from django.contrib import admin

from .models import Registrant, Location, LocationSummary


@admin.register(Registrant)
class RegistrantAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "created"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['name', 'city', 'province', 'short_code', 'registrant']
    list_filter = (
        'province',
        'city',
    )
