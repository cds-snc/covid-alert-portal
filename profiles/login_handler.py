from datetime import timedelta
from django.utils.timezone import now
from axes.handlers.database import AxesDatabaseHandler
from axes.signals import user_locked_out
from django.conf import settings

from .models import HealthcareFailedAccessAttempt, HealthcareUser


class HealthcareLoginHandler(AxesDatabaseHandler):
    def is_locked(self, request, credentials: dict = None) -> bool:
        locked = super().is_locked(request, credentials)
        # If AxesDatabaseHandler already returns locked, let's return it right now
        if locked:
            return True

        user = HealthcareUser.objects.get(email=credentials.get("username"))
        if user.blocked_until is not None and user.blocked_until >= now():
            return True

        # If not, let's check the double throttling strategy
        attempts = self.get_healthcareuser_failures(request, credentials)
        if attempts >= settings.AXES_SLOW_FAILURE_LIMIT:
            return True

        return False

    def user_login_failed(self, sender, credentials: dict, request=None, **kwargs):
        super().user_login_failed(sender, credentials, request, **kwargs)

        username = credentials.get("username")
        HealthcareFailedAccessAttempt.objects.create(username=username)

        attempts = self.get_healthcareuser_failures(request, credentials)
        if attempts >= settings.AXES_SLOW_FAILURE_LIMIT:
            request.axes_locked_out = True

            user_locked_out.send(
                "axes",
                request=request,
                username=username,
                ip_address=request.axes_ip_address,
            )

    def user_logged_in(self, sender, request, user, **kwargs):
        super().user_logged_in(sender, request, user, **kwargs)
        # Let's clean up the blocked_until field if set
        if user.blocked_until is not None:
            user.blocked_until = None
            user.save()

    def get_healthcareuser_failures(
        self, request: dict, credentials: dict = None
    ) -> int:
        username = credentials.get("username")
        threshold = timedelta(days=settings.AXES_SLOW_FAILURE_COOLOFF_TIME)
        return HealthcareFailedAccessAttempt.objects.filter(
            username=username, time__gte=now() - threshold
        ).count()
