from django.apps import apps
from django.test import TestCase
from django.urls import reverse

from .apps import AboutConfig


class AboutConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AboutConfig.name, "about")
        self.assertEqual(apps.get_app_config("about").name, "about")


class AboutView(TestCase):
    def test_about_covid_alert_page(self):
        response = self.client.get(reverse("about:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>COVID Alert</h1>", html=True)
        # check that the side nav link is active
        self.assertContains(
            response, '<a class="active" href="/en/about/">COVID Alert</a>', html=True
        )

    def test_about_create_account_page(self):
        response = self.client.get(reverse("about:create_account"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Log in to the portal</h1>", html=True)
        self.assertContains(
            response,
            '<a class="active" href="/en/about/create-an-account">Log in to the portal</a>',
            html=True,
        )

    def test_about_one_time_keys_page(self):
        response = self.client.get(reverse("about:one_time_keys"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>One-time keys</h1>", html=True)
        self.assertContains(
            response,
            '<a class="active" href="/en/about/one-time-keys">One-time keys</a>',
            html=True,
        )

    def test_about_give_a_key_page(self):
        response = self.client.get(reverse("about:give_a_key"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Give a key</h1>", html=True)
        self.assertContains(
            response,
            '<a class="active" href="/en/about/give-a-key">Give a key</a>',
            html=True,
        )

    def test_about_help_patient_enter_key_page(self):
        response = self.client.get(reverse("about:help_patient_enter_key"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Help patient enter key</h1>", html=True)
        self.assertContains(
            response,
            '<a class="active" href="/en/about/help-patient-enter-key">Help patient enter key</a>',
            html=True,
        )

    def test_about_admin_accounts_page(self):
        response = self.client.get(reverse("about:admin_accounts"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Admin accounts</h1>", html=True)
        self.assertContains(
            response,
            '<a class="active" href="/en/about/admin-accounts">Admin accounts</a>',
            html=True,
        )
