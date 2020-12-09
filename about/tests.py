from django.apps import apps
from django.test import TestCase
from django.urls import reverse

from .apps import AboutConfig


class ContactConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AboutConfig.name, "about")
        self.assertEqual(apps.get_app_config("about").name, "about")
