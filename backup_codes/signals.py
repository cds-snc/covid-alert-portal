from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django_otp.plugins.otp_static.models import StaticToken

from announcements.models import Announcement
from .views import _remove_low_on_codes_notification
import waffle

User = get_user_model()


@receiver(post_delete, sender=StaticToken)
def add_low_on_tokens_notification(sender, instance, **kwargs):
    if waffle.switch_is_active("BACKUP_CODE"):
        users_static_codes_remaining = instance.device.token_set.all().count()
        if users_static_codes_remaining <= 1:
            # Remove existing notification for only 1 code remaining if it exists
            _remove_low_on_codes_notification(instance.device.user)

            print(
                "user exists: {}".format(
                    User.objects.filter(pk=instance.device.user.id).exists()
                )
            )
            print("--")
            print("get: {}".format(User.objects.get(pk=instance.device.user.id)))
            print("--")
            print(sender)
            print("--")
            print(instance)
            print("--")
            print(kwargs)
            print("--")
            # create announcement for user if the user still exists (eg, if the user has not been deleted by an admin)
            if User.objects.filter(pk=instance.device.user.id).exists():
                Announcement.objects.create(
                    title_en=f"You have {users_static_codes_remaining} security code{'s' if users_static_codes_remaining == 0 else ''} remaining.",
                    title_fr=f"Il vous reste {users_static_codes_remaining} code{'s' if users_static_codes_remaining == 0 else ''} de sécurité.",
                    content_en=f"To get more codes, visit <a href='/profiles/{instance.device.user.id}'>Your Account</a>",
                    content_fr=f"Pour obtenir plus de codes, visitez <a href='/profiles/{instance.device.user.id}'>Votre Compte</a>",
                    level="info",
                    for_user=instance.device.user,
                    is_active=True,
                )
