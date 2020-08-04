from datetime import timedelta
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from profiles.tests import AdminUserTestCase
from .models import COVIDKey


class KeyView(AdminUserTestCase):
    def test_key(self):
        """
        Login and then see the key page and one generated code
        """
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.get(reverse("key"))
        self.assertEqual(response.status_code, 302)

        self.login_2fa()

        response = self.client.get(reverse("key"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Give patient this key</h1>")
        self.assertContains(
            response, "<code>{}</code>".format(response.context["code"])
        )

    @override_settings(COVID_KEY_MAX_PER_USER_PER_DAY=1)
    def test_key_throttled(self):
        self.login()
        covid_key = COVIDKey()
        covid_key.created_by = self.user
        covid_key.expiry = timezone.now() + timedelta(days=1)
        covid_key.save()

        response = self.client.get(reverse("key"))
        self.assertContains(
            response, "You have hit your daily limit of code generation"
        )
