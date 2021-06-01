from datetime import timedelta
from django.apps import apps
from django.test import override_settings, Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.conf import settings

from profiles.models import HealthcareUser, HealthcareProvince
from profiles.tests import AdminUserTestCase, get_other_credentials

from portal.services import NotifyService
from portal import container

from .apps import CovidKeyConfig
from .models import COVIDKey
from .views import CodeView

User = get_user_model()


class CovidKeyConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(CovidKeyConfig.name, "covid_key")
        self.assertEqual(apps.get_app_config("covid_key").name, "covid_key")


class LandingView(AdminUserTestCase):
    def setUp(self):
        super().setUp()

    def test_landing_view_with_alert_perm(self):
        self.user.user_permissions.add(Permission.objects.get(codename="can_send_alerts"))
        self.login()
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Welcome to the COVID Alert portal</h1>")

    def test_landing_view_without_alert_perm(self):
        self.login()
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("start"))


class StartView(AdminUserTestCase):
    def setUp(self):
        super().setUp()

    def test_start_view(self):
        self.login()
        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>You’re logged in to give one-time keys</h1>")

    def test_generate_key_view(self):
        self.login()
        response = self.client.get(reverse("generate_key"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>When patient is ready, generate a key</h1>")


class KeyView(AdminUserTestCase):
    def test_key(self):
        """
        Login and then see the key page and one generated code
        """
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.post(reverse("key"))
        self.assertEqual(response.status_code, 302)

        self.login_2fa()

        response = self.client.post(reverse("key"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Give patient this key</h1>")
        self.assertContains(
            response, "<code>{}</code>".format(response.context["code"])
        )

    def test_key_redirects_on_get(self):
        """
        GET requests to the "/key" page will be redirected to "/start"
        """
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(reverse("key"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/en/start/")

    @override_settings(COVID_KEY_MAX_PER_USER=1)
    def test_key_throttled(self):
        previous_throttled_value = CodeView.throttled_limit
        CodeView.throttled_limit = settings.COVID_KEY_MAX_PER_USER
        self.login()
        covid_key = COVIDKey()
        covid_key.created_by = self.user
        covid_key.expiry = timezone.now() + timedelta(days=1)
        covid_key.save()

        response = self.client.post(reverse("key"))
        self.assertContains(
            response,
            "You are generating too many keys. Try again later.",
            status_code=403,
        )
        CodeView.throttled_limit = previous_throttled_value

    @override_settings(COVID_KEY_MAX_PER_USER=1)
    def test_key_throttled_for_another_user(self):
        previous_throttled_value = CodeView.throttled_limit
        CodeView.throttled_limit = settings.COVID_KEY_MAX_PER_USER
        self.login()
        covid_key = COVIDKey()
        covid_key.created_by = self.user
        covid_key.expiry = timezone.now() + timedelta(days=1)
        covid_key.save()

        response = self.client.post(reverse("key"))
        self.assertContains(
            response,
            "You are generating too many keys. Try again later.",
            status_code=403,
        )

        user2_credentials = get_other_credentials()
        get_user_model().objects.create_user(**user2_credentials)
        self.login(user2_credentials)
        response = self.client.get(reverse("key"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/en/start/")
        CodeView.throttled_limit = previous_throttled_value


class KeyViewCSRFEnabled(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=False)
        self.client = Client(enforce_csrf_checks=True)

    def test_CSRF_page_for_bad_posts(self):
        """
        GET requests to the "/key" page will be redirected to "/start"
        """
        self.client.login(
            username=self.credentials.get("email"),
            password=self.credentials.get("password"),
        )
        user = HealthcareUser.objects.get(email=self.credentials.get("email"))

        device = user.notifysmsdevice_set.first()
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

        response = self.client.post(reverse("key"))

        self.assertEqual(response.status_code, 403)


class OtkSmsViewTests(AdminUserTestCase):
    def setUp(self):
        super().setUp()
        container.notify_service.override(NotifyService())  # Prevent sending emails/SMS

        # Ensure that manitoba has sms enabled (test user is located in manitoba)
        manitoba = HealthcareProvince.objects.get(name="Manitoba")
        manitoba.sms_enabled = True
        manitoba.save()

    def test_otk_sms_view_no_key(self):
        """
        Test that this view redirects back to start when there is no OTK
        cached in the request session
        """
        self.login()
        response = self.client.get(reverse("otk_sms"))
        self.assertEqual(response.status_code, 302)

    def test_otk_sms_view_with_key(self):
        """
        Test that this view is rendered when there is an OTK cached
        """
        self.login()
        self.client.post(
            reverse("key")
        )  # generate a key so it can be cached in session
        response = self.client.get(reverse("otk_sms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>If patient gives permission, text this key to their phone</h1>",
        )

    def test_otk_sms_view_disabled_province(self):
        """
        Test that a province that's opted out of SMS cannot reach the sms_view
        """
        credentials = {
            "email": "test3@test.com",
            "name": "testuser3",
            "province": HealthcareProvince.objects.get(abbr="QC"),
            "is_admin": True,
            "password": "testpassword",
            "phone_number": "+12125552368",
        }
        User.objects.create_user(**credentials)
        self.login(credentials)
        self.client.post(
            reverse("key")
        )  # generate a key so it can be cached in session
        response = self.client.get(reverse("otk_sms"))
        self.assertEqual(response.status_code, 302)  # Redirect to start

    def test_otk_sms_view_submit_error(self):
        """
        Test that we see an error message if mismatching phone numbers are entered
        """
        self.login()
        self.client.post(
            reverse("key")
        )  # generate a key so it can be cached in session
        response = self.client.post(
            reverse("otk_sms"),
            {"phone_number": "+12125551111", "phone_number2": "+12125552222"},
        )
        self.assertContains(response, "Phone numbers must match")

    def test_otk_sms_view_submit_redirect(self):
        """
        Test that we're redirected to otk_sms_sent on form submission
        """
        self.login()
        self.client.post(
            reverse("key")
        )  # generate a key so it can be cached in session
        response = self.client.post(
            reverse("otk_sms"),
            {"phone_number": "+12125552368", "phone_number2": "+12125552368"},
        )
        self.assertEqual(response.status_code, 302)

    def test_otk_sms_sent_view(self):
        """
        Test that the otk_sms_sent view is rendered
        """
        self.login()
        self.client.post(
            reverse("key")
        )  # generate a key so it can be cached in session
        response = self.client.get(
            reverse("otk_sms_sent", kwargs={"phone_number": "+12125552368"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Check patient received this key</h1>")
