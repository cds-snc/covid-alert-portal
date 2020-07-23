from django.contrib.admin.sites import AdminSite


class Admin2FASite(AdminSite):
    name = "2faadmin"
    login_template = "admin/login-disabled.html"

    def has_permission(self, request):
        # Let's make sure 2fa is enabled and confirmed on this user
        return super().has_permission(request) and request.user.is_verified()
