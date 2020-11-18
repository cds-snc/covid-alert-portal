from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from portal.mixins import ProvinceAdminMixin


class ProvinceAdminEditMixin(ProvinceAdminMixin):
    def test_func(self):
        # 404 if bad user ID
        profile_user = get_object_or_404(get_user_model(), pk=self.kwargs["pk"])

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
