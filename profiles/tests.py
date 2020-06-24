from django.test import TestCase, Client

from django.urls import reverse
from django.utils import translation


class StartView(TestCase):
    def test_start(self):
        """
        Just see the start page
        """
        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Generate code for Exposure Notification app")


class CodeView(TestCase):
    def test_code(self):
        """
        Just see the code page and one code
        """
        response = self.client.get(reverse("code"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Provide patient with code")
        self.assertContains(
            response, '<code id="big-code">{}</code>'.format(response.context["code"])
        )


class i18nTestView(TestCase):
    def test_root_with_accept_language_header_fr(self):
        """
        Test we end up on French start page from root url if "Accept-Language" header is "fr"
        """
        client = Client(HTTP_ACCEPT_LANGUAGE="fr",)
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/fr/start/")

    def test_root_with_accept_language_header_en(self):
        """
        Test we end up on English start page from root url if "Accept-Language" header is "en"
        """
        client = Client(HTTP_ACCEPT_LANGUAGE="en",)
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/start/")

    def test_root_without_accept_language_header(self):
        """
        Test we end up on English start page from root url if no "Accept-Language" header exists
        """
        client = Client()
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/start/")

    def test_start_with_language_setting_fr(self):
        """
        Test we end up on French start page from start url "fr" is active language
        """
        translation.activate("fr")
        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/fr/start/")

    def test_start_with_language_setting_en(self):
        """
        Test we end up on English start page from start url "en" is active language
        """
        translation.activate("en")
        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/start/")
