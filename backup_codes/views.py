from django.views.generic import ListView
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken

from waffle.mixins import WaffleSwitchMixin

from portal.mixins import Is2FAMixin


class BackupCodeListView(WaffleSwitchMixin, Is2FAMixin, ListView):
    waffle_switch = "BACKUP_CODE"
    template_name = "backup_codes/backup_codes_list.html"
    context_object_name = "backup_code_list"

    def setup(self, request, *args, **kwargs):
        self.recreate_backup_codes(request)

        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        return get_user_static_device(self, self.request.user).token_set.all()

    def recreate_backup_codes(self, request):
        devices = get_user_static_device(self, request.user)
        if devices:
            devices.token_set.all().delete()
        else:
            devices = StaticDevice.objects.create(
                user=request.user, name="Static_Security_Codes"
            )
        for n in range(5):
            security_code = StaticToken.random_token()
            devices.token_set.create(token=security_code)


def get_user_static_device(self, user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, StaticDevice):
            return device
