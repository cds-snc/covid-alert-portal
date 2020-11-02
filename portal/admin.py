from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group

from waffle.models import Flag, Sample


class Admin2FASite(AdminSite):
    name = "2faadmin"
    login_template = "admin/login-disabled.html"

    def has_permission(self, request):
        # Let's make sure 2fa is enabled and confirmed on this user
        return super().has_permission(request) and request.user.is_verified()


# unregister the Group model from admin.
admin.site.unregister(Group)

# unregister the Flag, Sample models from django-admin.
admin.site.unregister(Flag)
admin.site.unregister(Sample)
