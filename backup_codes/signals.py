from django.db.models.signals import post_delete
from django.dispatch import receiver

from django_otp.plugins.otp_static.models import StaticToken
from django.urls import reverse_lazy

from announcements.models import Announcement
from .views import _remove_low_on_codes_notification


@receiver(post_delete, sender=StaticToken)
def add_low_on_tokens_notification(sender, instance, **kwargs):
    users_static_codes_remaining = instance.device.token_set.all().count()
    if users_static_codes_remaining <= 1:
        # Remove existing notification for only 1 code remaining if it exists
        _remove_low_on_codes_notification(instance.device.user)

        users_profile = reverse_lazy(
            "user_profile", kwargs={"pk": instance.device.user.id}
        )
        Announcement.objects.create(
            title_en=f"You have {users_static_codes_remaining} security code remaining.",
            title_fr=f"Il vous reste {users_static_codes_remaining} code de sécurité.",
            content_en=f"To get more codes, visit <a href='{users_profile}'>Your Account</a>",
            content_fr=f"Pour obtenir plus de codes, visitez <a href='{users_profile}'>Votre Compte</a>",
            level="info",
            for_user=instance.device.user,
            display=True,
        )
