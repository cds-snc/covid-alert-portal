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

    def test_user_can_get_security_codes_on_account_page(self):
        self.login()
        response = self.client.get(reverse("user_profile", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0 codes remaining", html=True)
        ## get security codes button
        self.assertContains(
            response, '<button type="submit" class="link">Get security codes</button>'
        )

    def test_user_can_view_codes_row_on_account_page(self):
        self.login()
        # generate codes
        self.client.post(reverse("backup_codes"))

        response = self.client.get(reverse("user_profile", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5 codes remaining", html=True)
        ## view security codes link
        self.assertContains(
            response, '<a href="/en/backup-codes">View security codes</a>'
        )

    def test_user_redirected_from_backup_codes_page_without_codes(self):
        self.login()
        response = self.client.get(reverse("backup_codes"))
        self.assertRedirects(response, "/en/profiles/{}".format(self.credentials["id"]))

    def test_user_can_generate_5_security_codes(self):
        self.login()
        response = self.client.post(reverse("backup_codes"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Security codes</h1>")

        device = StaticDevice.objects.get(user__id=self.user.id)
        self.assertEqual(len(device.token_set.all()), 5)

    def test_old_security_codes_invalid_if_new_security_codes_generated(self):
        self.login()
        response = self.client.post(reverse("backup_codes"))
        self.assertRedirects(response, "/en/backup-codes")

        old_codes = [
            t.token
            for t in StaticDevice.objects.get(user__id=self.user.id).token_set.all()
        ]

        response = self.client.post(reverse("backup_codes"))
        self.assertRedirects(response, "/en/backup-codes")
        new_codes = [
            t.token
            for t in StaticDevice.objects.get(user__id=self.user.id).token_set.all()
        ]

        for code in old_codes:
            self.assertNotIn(code, new_codes)

    def test_user_codes_HTML(self):
        self.login()
        response = self.client.post(reverse("backup_codes"), follow=True)
        self.assertRedirects(response, "/en/backup-codes")
        self.assertContains(response, "<h1>Security codes</h1>")
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
