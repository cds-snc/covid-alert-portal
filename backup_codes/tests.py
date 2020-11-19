from time import sleep
from django.apps import apps
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from profiles.utils import generate_2fa_code

from django_otp.plugins.otp_static.models import StaticDevice
from invitations.models import Invitation
from profiles.models import HealthcareProvince
from waffle.models import Switch

from profiles.tests import AdminUserTestCase

from .apps import BackupCodesConfig


class BackupCodesConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(BackupCodesConfig.name, "backup_codes")
        self.assertEqual(apps.get_app_config("backup_codes").name, "backup_codes")


class BackupCodesView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)
        Switch.objects.create(name="BACKUP_CODE", active=True)

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
        self.assertContains(response, "10 codes remaining", html=True)
        ## view security codes link
        self.assertContains(
            response, '<a href="/en/backup-codes">View security codes</a>'
        )

    def test_user_redirected_from_backup_codes_page_without_codes(self):
        self.login()
        response = self.client.get(reverse("backup_codes"))
        self.assertRedirects(response, "/en/profiles/{}".format(self.credentials["id"]))

    def test_user_can_generate_10_security_codes(self):
        self.login()
        response = self.client.post(reverse("backup_codes"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Security codes</h1>")

        device = StaticDevice.objects.get(user__id=self.user.id)
        self.assertEqual(len(device.token_set.all()), 10)

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
                    token[:4].upper(), token[-4:].upper()
                ),
            )

    def test_user_codes_empty_HTML(self):
        self.login()
        response = self.client.post(reverse("backup_codes"), follow=True)
        device = StaticDevice.objects.get(user__id=self.user.id)
        # delete all but 1 code
        for _ in range(len(device.token_set.all()) - 1):
            device.token_set.last().delete()
        self.assertEqual(len(device.token_set.all()), 1)

        # make sure it says "1 code remaining"
        response = self.client.get(reverse("user_profile", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 code remaining", html=True)

        # make sure there are 9 empty list items
        response = self.client.get(reverse("backup_codes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<li aria-hidden="true" class="empty"><span></span></li>',
            count=9,
            html=True,
        )


class BackupCodesLogin(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)
        Switch.objects.create(name="BACKUP_CODE", active=True)
        self.ensure_codes_created()
        self.logout()

    def ensure_codes_created(self):
        self.login(login_2fa=True)
        self.client.post(reverse("backup_codes"), follow=True)

    def logout(self):
        self.client.logout()

    def test_user_can_login_with_backup_code(self):
        self.login(login_2fa=False)

        #  Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)

        # Get backup code
        static_device = self.user.staticdevice_set.first()
        token = static_device.token_set.first().token

        # Submit backup code
        response = self.client.post(reverse("login_2fa"), {"code": token}, follow=True)

        # Check if we are now verified
        self.assertTrue(response.context["user"].is_verified())

    def test_user_can_login_with_backup_code_case_insensitive(self):
        self.login(login_2fa=False)

        #  Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)

        # Get backup code
        static_device = self.user.staticdevice_set.first()
        token = static_device.token_set.first().token

        # uppercase backup code
        token = token.upper()

        # Submit backup code
        response = self.client.post(reverse("login_2fa"), {"code": token}, follow=True)

        # Check if we are now verified
        self.assertTrue(response.context["user"].is_verified())

    def test_user_can_login_with_backup_code_whitespace(self):
        self.login(login_2fa=False)

        #  Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)

        # Get backup code
        static_device = self.user.staticdevice_set.first()
        token = static_device.token_set.first().token

        # add leading and trailing whitespace, and a space in the middle
        token = " {} {} ".format(token[:4], token[4:])

        # Submit backup code
        response = self.client.post(reverse("login_2fa"), {"code": token}, follow=True)

        # Check if we are now verified
        self.assertTrue(response.context["user"].is_verified())

    def test_user_can_login_with_sms_code(self):
        self.login(login_2fa=False)
        generate_2fa_code(self.user)

        #  Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)

        # Get backup code
        sms_device = self.user.notifysmsdevice_set.last()
        token = sms_device.token

        # Submit backup code
        post_data = {"code": token}
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )

        # Check if we are now verified
        self.assertTrue(response.context["user"].is_verified)


class BackupCodesHelp(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=False)
        Switch.objects.create(name="BACKUP_CODE", active=True)
        self.inviter_credentials = {
            "email": "inviter@test.com",
            "name": "InviterUser",
            "province": HealthcareProvince.objects.get(abbr="MB"),
            "is_admin": True,
            "password": "superdupercomplex_To_Infinity_and_Beyond",
            "phone_number": "+12125552368",
        }
        User = get_user_model()
        self.inviter = User.objects.create_user(**self.inviter_credentials)
        self.invite = Invitation.create(
            self.user.email, inviter=self.inviter, sent=timezone.now()
        )
        self.invite.accepted = True

    def test_users_admin_displayed_on_backup_code_help_page(self):
        self.login(login_2fa=False)
        response = self.client.get(reverse("backup_codes_help"))
        self.assertContains(response, self.inviter.email)

    def test_generic_admin_displayed_on_backup_code_page_when_inviter_doesnt_exist(
        self,
    ):
        # Delete inviter
        User = get_user_model()
        User.objects.filter(email__exact=self.inviter.email).delete()

        self.login(login_2fa=False)
        response = self.client.get(reverse("backup_codes_help"))
        self.assertContains(response, "assistance+healthcare@cds-snc.ca")


class BackupCodesRedirect(TestCase):
    def setUp(self):
        super().setUp()
        Switch.objects.create(name="BACKUP_CODE", active=True)
        self.user_credentials = {
            "email": "user1@test.com",
            "name": "No Phone User",
            "province": HealthcareProvince.objects.get(abbr="MB"),
            "is_admin": True,
            "password": "superdupercomplex_To_Infinity_and_Beyond",
        }
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_credentials)

    def test_user_redirected_to_signup_if_no_mobile_or_static_codes(self):
        self.client.login(
            username=self.user_credentials.get("email"),
            password=self.user_credentials.get("password"),
        )
        response = self.client.get(reverse("login_2fa"), follow=True)
        self.assertRedirects(response, "/en/signup-2fa/")


class BackupCodesSignupView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)
        Switch.objects.create(name="BACKUP_CODE", active=True)

    def test_redirect_to_login_backup_codes_signup_view(self):
        response = self.client.get(reverse("signup_backup_codes"))
        self.assertRedirects(response, "/en/login/?next=/en/signup/backup-codes")

    def test_redirect_to_start_backup_codes_signup_view_after_login(self):
        self.login()
        response = self.client.get(reverse("signup_backup_codes"))
        self.assertRedirects(response, "/en/start/")

    def test_backup_codes_signup_view_after_setting_referrer(self):
        self.login()
        # this header assumes they have come from the "/2fa-signup" page
        # syntax here: https://stackoverflow.com/a/31903154
        headers = {"HTTP_REFERER": reverse("signup_2fa")}
        response = self.client.get(reverse("signup_backup_codes"), **headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>No mobile phone?</h1>")

        device = StaticDevice.objects.get(user__id=self.user.id)
        self.assertEqual(len(device.token_set.all()), 10)


class BackupCodesLockout(BackupCodesLogin):
    def check_throttle_failure_count(self, devices):
        count = 0
        for device in devices:
            count = count + device.throttling_failure_count

        return count

    @override_settings(BACKUP_CODES_LOCKOUT_LIMIT=2)
    def test_lockout_of_backup_codes_with_sms_device(self):
        # Only test the SMS codes
        user = self.user
        user.staticdevice_set.all().delete()
        self.login(login_2fa=False)
        generate_2fa_code(self.user)
        # Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)
        # Set bad token code
        token = "ImBadToken"
        # Submit backup code
        post_data = {"code": token}
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        # Check if we are now verified
        self.assertFormError(response, "form", "code", "You entered the wrong code.")
        # Pause to ensure second request isn't throttled.
        sleep(2)
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        self.assertRedirects(response, "/en/login/")
        # Test to ensure the tocken failures have been reset.
        self.assertEqual(
            self.check_throttle_failure_count(user.notifysmsdevice_set.all()), 0
        )
        self.assertEqual(
            self.check_throttle_failure_count(user.staticdevice_set.all()), 0
        )

    @override_settings(BACKUP_CODES_LOCKOUT_LIMIT=2)
    def test_lockout_of_backup_codes_with_static_device(self):
        # Only test the Static Codes
        user = self.user
        user.notifysmsdevice_set.all().delete()
        self.login(login_2fa=False)
        # Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)
        # Set bad token code
        token = "ImBadToken"
        # Submit backup code
        post_data = {"code": token}
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        # Check if we are now verified
        self.assertFormError(response, "form", "code", "You entered the wrong code.")
        # Pause to ensure second request isn't throttled.
        sleep(2)
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        self.assertRedirects(response, "/en/login/")
        # Test to ensure the tocken failures have been reset.
        self.assertEqual(
            self.check_throttle_failure_count(user.notifysmsdevice_set.all()), 0
        )
        self.assertEqual(
            self.check_throttle_failure_count(user.staticdevice_set.all()), 0
        )

    def test_backup_code_attempts_are_being_throttled_with_sms(self):
        # Remove any Static codes if they exist
        self.user.staticdevice_set.all().delete()
        self.login(login_2fa=False)
        # Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)
        # Set bad token code
        token = "ImBadToken"
        # Submit backup code
        post_data = {"code": token}
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        # Check if we are now verified
        self.assertFormError(response, "form", "code", "You entered the wrong code.")
        # Pause to ensure second request isn't throttled.
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        self.assertFormError(response, "form", "code", "Please try again later.")

    def test_backup_code_attempts_are_being_throttled_with_static(self):
        # Remove any Static codes if they exist
        self.user.notifysmsdevice_set.all().delete()
        self.login(login_2fa=False)
        # Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)
        # Set bad token code
        token = "ImBadToken"
        # Submit backup code
        post_data = {"code": token}
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        # Check if we are now verified
        self.assertFormError(response, "form", "code", "You entered the wrong code.")
        # Pause to ensure second request isn't throttled.
        response = self.client.post(
            reverse("login_2fa"),
            post_data,
            follow=True,
        )
        self.assertFormError(response, "form", "code", "Please try again later.")
