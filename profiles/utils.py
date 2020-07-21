from .models import HealthcareUser


def generate_2fa_code(user: HealthcareUser):
    sms_devices = user.notifysmsdevice_set.all()
    for sms_device in sms_devices:
        sms_device.generate_challenge()
