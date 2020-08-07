from datetime import timedelta
from django.test import override_settings, Client
from django.urls import reverse
from django.utils import timezone
from django_otp import DEVICE_ID_SESSION_KEY
from django.contrib.auth import get_user_model

from profiles.tests import AdminUserTestCase, get_other_credentials
from .models import COVIDKey
from profiles.models import HealthcareUser


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

    @override_settings(COVID_KEY_MAX_PER_USER_PER_DAY=1)
    def test_key_throttled(self):
        self.login()
        covid_key = COVIDKey()
        covid_key.created_by = self.user
        covid_key.expiry = timezone.now() + timedelta(days=1)
        covid_key.save()

        response = self.client.post(reverse("key"))
        self.assertContains(
            response, "You have hit your daily limit of code generation"
        )

    @override_settings(COVID_KEY_MAX_PER_USER_PER_DAY=1)
    def test_key_throttled_for_another_user(self):
        self.login()
        covid_key = COVIDKey()
        covid_key.created_by = self.user
        covid_key.expiry = timezone.now() + timedelta(days=1)
        covid_key.save()

        response = self.client.post(reverse("key"))
        self.assertContains(
            response, "You have hit your daily limit of code generation"
        )

        user2_credentials = get_other_credentials()
        get_user_model().objects.create_user(**user2_credentials)
        self.login(user2_credentials)
        response = self.client.get(reverse("key"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/en/start/")


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
