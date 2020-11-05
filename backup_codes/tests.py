from django.apps import apps
from django.test import TestCase
from django.urls import reverse

from django_otp.plugins.otp_static.models import StaticDevice

from profiles.tests import AdminUserTestCase

from .apps import BackupCodesConfig


class BackupCodesConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(BackupCodesConfig.name, "backup_codes")
        self.assertEqual(apps.get_app_config("backup_codes").name, "backup_codes")


class SecurityCodeView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_user_can_view_security_codes_row_on_account_page(self):
        self.login()
        response = self.client.get(reverse("user_profile", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        ## security codes link is present
        self.assertContains(response, '<a href="/en/backup-codes">')

    def test_user_can_generate_5_security_codes(self):
        self.login()
        response = self.client.get(reverse("backup_codes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Security Codes</h1>")

        device = StaticDevice.objects.get(user__id=self.user.id)
        self.assertEqual(len(device.token_set.all()), 5)

    def test_old_security_codes_invalid_if_new_security_codes_generated(self):
        self.login()
        response = self.client.get(reverse("backup_codes"))
        self.assertEqual(response.status_code, 200)

        old_codes = [
            t.token
            for t in StaticDevice.objects.get(user__id=self.user.id).token_set.all()
        ]

        response = self.client.get(reverse("backup_codes"))
        self.assertEqual(response.status_code, 200)
        new_codes = [
            t.token
            for t in StaticDevice.objects.get(user__id=self.user.id).token_set.all()
        ]

        for code in old_codes:
            self.assertNotIn(code, new_codes)

    def test_user_codes_HTML(self):
        self.login()
        response = self.client.get(reverse("backup_codes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Security Codes</h1>")
        device = StaticDevice.objects.get(user__id=self.user.id)

        tokens = [t.token for t in device.token_set.all()]

        for token in tokens:
            self.assertContains(
                response,
                '<span class="visually-hidden">{}</span>'.format(
                    " ".join(token.upper())
                ),
            )
            self.assertContains(
                response,
                '<span aria-hidden="true"><span>{}</span><span>{}</span>'.format(
                    token[:4], token[-4:]
                ),
            )
