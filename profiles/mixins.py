from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .models import HealthcareUser


class ProvinceAdminViewMixin(UserPassesTestMixin):
    def test_func(self):
        # if logged in user is superuser, allow operation
        if self.request.user.is_superuser:
            return True

        # 404 if bad user ID
        profile_user = get_object_or_404(HealthcareUser, pk=self.kwargs["pk"])

        # if same user, allow operation
        if self.request.user.id == profile_user.id:
            return True

        # Don't return superuser profile pages
        if profile_user.is_superuser:
            return False

        # if admin user, return users from the same province
        if (
            self.request.user.is_admin
            and self.request.user.province.id == profile_user.province.id
        ):
            return True

        return False


class ProvinceAdminEditMixin(ProvinceAdminViewMixin):
    def test_func(self):
        # 404 if bad user ID
        profile_user = get_object_or_404(HealthcareUser, pk=self.kwargs["pk"])

        # admins can't edit other admins
        if (
            not self.request.user.is_superuser
            and self.request.user.is_admin
            and profile_user.is_admin
        ):
            return False

        return super().test_func()


class ProvinceAdminDeleteMixin(ProvinceAdminEditMixin):
    def test_func(self):
        # you can't delete yourself
        if self.request.user.id == self.kwargs["pk"]:
            return False

        return super().test_func()


class EditPasswordMixin(UserPassesTestMixin):
    def test_func(self):
        # you can't change someone else's password
        if self.request.user.id != self.kwargs["pk"]:
            return False

        return True
