from django.db.models.signals import post_delete
from django.dispatch import receiver

from django_otp.plugins.otp_static.models import StaticToken

from announcements.models import Announcement
from .views import _remove_low_on_codes_notification

from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_delete, sender=User)
def remove_any_outstanding_announcements_to_be_created(sender, instance, **kwargs):
    # Remove any announcements for the user that were just created because of low code signal
    Announcement.objects.filter(for_user=instance).delete()


@receiver(post_delete, sender=StaticToken)
def add_low_on_tokens_notification(sender, instance, **kwargs):
    for_user = User.objects.get(id=instance.device.user.id)
    users_static_codes_remaining = instance.device.token_set.all().count()

    if users_static_codes_remaining <= 1:
        # Remove existing notification for only 1 code remaining if it exists
        _remove_low_on_codes_notification(for_user)

        Announcement.objects.create(
            title_en=f"You have {users_static_codes_remaining} log in code{'s' if users_static_codes_remaining == 0 else ''} left.",
            title_fr=f"Il vous reste {users_static_codes_remaining} code{'s' if users_static_codes_remaining == 0 else ''} de sécurité.",
            content_en=f"To get more codes, visit ‘<a href='/profiles/{for_user.id}'>Manage your Account</a>’",
            content_fr=f"Pour obtenir plus de codes, visitez <a href='/profiles/{for_user.id}'>Gérer votre compte</a>",
            level="info",
            for_user=for_user,
            is_active=True,
        )
