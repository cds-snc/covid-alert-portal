from django.apps import apps
from django.test.testcases import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from profiles.tests import AdminUserTestCase, get_other_credentials

from .apps import AnnouncementsConfig
from .models import Announcement

User = get_user_model()


class AnnouncementsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AnnouncementsConfig.name, "announcements")
        self.assertEqual(apps.get_app_config("announcements").name, "announcements")

class AnnoncementsSiteWide(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)
        self.user2_credentials = get_other_credentials(is_admin=False)
        self.user2 = User.objects.create_user(**self.user2_credentials)
        Announcement.objects.create(
            title_en="Test for Site Wide",
            title_fr="Voici un test Site Wide",
            level="info",
            display=True,
            site_wide=True
        )
    def test_site_wide_is_visible_by_all(self):

        # First user can see message
        self.login()
        response = self.client.get(reverse("start"))
        self.assertContains(
            response,
            '<div class="title">Test for Site Wide</div>'
        )
        self.client.logout()

        # Second user can see message
        self.login(self.user2_credentials)
        response = self.client.get(reverse("start"))
        self.assertContains(
            response,
            '<div class="title">Test for Site Wide</div>'
        )

    def test_site_wide_is_visible_on_multiple_pages(self):
        self.login()
        # Page 1
        response = self.client.get(reverse("welcome"))
        self.assertContains(
            response,
            '<div class="title">Test for Site Wide</div>'
        )
        # Page 2
        response = self.client.get(reverse("start"))
        self.assertContains(
            response,
            '<div class="title">Test for Site Wide</div>'
        )
        # Page 3
        response = self.client.post(reverse("key"))
        self.assertContains(
            response,
            '<div class="title">Test for Site Wide</div>'
        )
