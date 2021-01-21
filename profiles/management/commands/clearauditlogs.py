from django.core.management.base import BaseCommand
from axes.models import AccessAttempt, AccessLog
from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Removing expired audit logs")
        delta = timezone.now() - timedelta(days=180)
        AccessAttempt.objects.filter(attempt_time__lt=delta).delete()
        AccessLog.objects.filter(attempt_time__lt=delta).delete()
        RequestEvent.objects.filter(datetime__lt=delta).exclude(
            url__in=["/en/key/", "/fr/key/"]
        ).delete()
        LoginEvent.objects.filter(datetime__lt=delta).delete()
        CRUDEvent.objects.filter(datetime__lt=delta).exclude(
            object_repr__startswith="COVIDKey object"
        ).delete()
