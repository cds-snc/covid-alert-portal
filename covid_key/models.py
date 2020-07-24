from uuid import uuid4
from django.db import models
from django.conf import settings


class COVIDKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    key = models.CharField(max_length=12, null=False)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING, related_name="+"
    )
