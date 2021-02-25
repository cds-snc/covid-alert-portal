from django.contrib import admin


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "start_date", "end_date", "created_date", "created_by", "severity", "location"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
