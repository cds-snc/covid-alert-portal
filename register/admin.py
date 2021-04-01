from django.contrib import admin

from .models import Registrant, Location


# Register your models here.
class RegistrantAdmin(admin.ModelAdmin):
    list_display = ["id", "email"]


class LocationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "city", "province"]


admin.site.register(Registrant, RegistrantAdmin)
admin.site.register(Location, LocationAdmin)
