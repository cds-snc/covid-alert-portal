from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import HealthcareUser


class ProvinceAdminManageMixin(UserPassesTestMixin):
    def test_func(self):
        # 404 if bad user ID
        profile_user = get_object_or_404(HealthcareUser, pk=self.kwargs["pk"])

        # if logged in user is superuser, return profile
        if self.request.user.is_superuser:
            return True

        # if same user, return profile
        if self.request.user.id == profile_user.id:
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
        if self.request.user.id == self.kwargs["pk"]:
            return False

        return super().test_func()


class IsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        # allow if superuser or admin
        if self.request.user.is_superuser or self.request.user.is_admin:
            return True

        return False


class Is2FAMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated and using 2FA."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not request.user.is_verified():
            return redirect_to_login(
                request.get_full_path(),
                settings.OTP_LOGIN_URL,
                self.get_redirect_field_name(),
            )

        return super().dispatch(request, *args, **kwargs)
