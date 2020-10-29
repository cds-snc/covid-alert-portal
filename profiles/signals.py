from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import HealthcareUser


@receiver(pre_save, sender=HealthcareUser)
def _save_previous_email(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = HealthcareUser.objects.get(pk=instance.id)
    except HealthcareUser.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=HealthcareUser)
def update_2fa(sender, instance, created, **kwargs):
    if not created and instance._pre_save_instance.phone_number:
        # Tries to update the sms device that belongs to the previous number
        # with the new number
        if isinstance(instance._pre_save_instance.phone_number, str):
            old_number = instance._pre_save_instance.phone_number
        else:
            old_number = instance._pre_save_instance.phone_number.as_e164

        if isinstance(instance.phone_number, str):
            new_number = instance.phone_number
        else:
            new_number = instance.phone_number.as_e164

        if old_number != new_number:
            sms_device = instance.notifysmsdevice_set.get(
                number=old_number, user=instance
            )
            if sms_device:
                sms_device.number = new_number
                sms_device.save()
    else:
        if instance.phone_number:
            sms_device = instance.notifysmsdevice_set.create()
            sms_device.number = instance.phone_number.as_e164
            sms_device.save()
