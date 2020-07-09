from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.shortcuts import get_object_or_404

from .models import HealthcareUser


class ProvinceAdminManageMixin(UserPassesTestMixin):
    def test_func(self):
        # 404 if bad user ID
        profile_user = get_object_or_404(HealthcareUser, pk=self.kwargs["pk"])

        # if logged in user is superuser, return profile
        if self.request.user.is_superuser:
            return True

        # if same user, return profile
        if self.request.user.id == int(profile_user.id):
            return True

        # Don't return superuser profile pages
        if profile_user.is_superuser:
            return False

        # if admin user from same province, return profile
        if (
            self.request.user.is_admin
            and self.request.user.province.id == profile_user.province.id
        ):
            return True

        return False


class ProvinceAdminDeleteMixin(ProvinceAdminManageMixin):
    def test_func(self):
        # id can't be yourself
        if self.request.user.id == int(self.kwargs["pk"]):
            return False

        return super().test_func()


class IsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        # allow if superuser or admin
        if self.request.user.is_superuser or self.request.user.is_admin:
            return True

        return False


class Is2FAMixin(AccessMixin):
    """Verify that the current user is authenticated and using 2FA."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_verified() or False:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
