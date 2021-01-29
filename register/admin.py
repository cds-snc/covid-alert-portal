from django.contrib import admin

from .models import Registrant


# Register your models here.
class RegistrantAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email"]


admin.site.register(Registrant, RegistrantAdmin)
