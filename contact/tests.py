from django.apps import apps
from django.test import TestCase
from django.urls import reverse

from .forms import ContactForm
from .apps import ContactConfig


class ContactConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ContactConfig.name, "contact")
        self.assertEqual(apps.get_app_config("contact").name, "contact")


class ContactView(TestCase):
    def test_contact_empty_feedback(self):
        response = self.client.get(reverse("contact:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "")

        post_data = {
            "name": "dummy name",
            "email": "test@test.com",
        }

        response = self.client.post(
            reverse("contact:index"),
            post_data,
        )
        self.assertContains(response, ContactForm.FEEDBACK_MESSAGE)

    def test_contact_valid(self):
        response = self.client.get(reverse("contact:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "")

        post_data = {
            "name": "dummy name",
            "email": "test@test.com",
            "feedback": "[test please delete] feedback",
        }

        response = self.client.post(
            reverse("contact:index"),
            post_data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("contact:success"))
