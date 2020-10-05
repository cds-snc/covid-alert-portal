from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now
from datetime import timedelta


class ThrottledMixin:
    throttled_lookup_user_field = "created_by"
    throttled_lookup_date_field = "created_at"
    throttled_model = None
    throttled_limit = None
    throttled_time_range = None

    def dispatch(self, *args, **kwargs):
        self._check()

        filter_kwargs = {
            f"{self.throttled_lookup_user_field}": self.request.user.id,
            f"{self.throttled_lookup_date_field}__gte": now()
            - timedelta(seconds=self.throttled_time_range),
        }
        count = self.throttled_model.objects.filter(**filter_kwargs).count()
        if count >= self.throttled_limit:
            return self.limit_reached()

        return super().dispatch(*args, **kwargs)

    def limit_reached(self):
        return render(self.request, "throttled/locked.html", status=403)

    def _check(self):
        if self.throttled_model is None:
            raise ImproperlyConfigured(
                "Class using ThrottledMixin should always provide a throttled_model"
            )
        if self.throttled_limit is None:
            raise ImproperlyConfigured(
                "Class using ThrottledMixin should always provide a throttled_limit"
            )
        if self.throttled_time_range is None:
            raise ImproperlyConfigured(
                "Class using ThrottledMixin should always provide a throttled_time_range in seconds"
            )

        if hasattr(self.throttled_model, self.throttled_lookup_user_field) is False:
            raise ImproperlyConfigured(
                f"The model passed to ThrottledMixin ({self.throttled_model}) has no field {self.throttled_lookup_user_field} for the look up."
            )

        if hasattr(self.throttled_model, self.throttled_lookup_date_field) is False:
            raise ImproperlyConfigured(
                f"The model passed to ThrottledMixin ({self.throttled_model}) has no field {self.throttled_lookup_date_field} for the look up."
            )


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


class IsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        # allow if superuser or admin
        if self.request.user.is_superuser or self.request.user.is_admin:
            return True

        return False
