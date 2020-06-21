from django.test import TestCase

from django.urls import reverse


class StartView(TestCase):
    def test_start(self):
        """
        Just see the start page
        """
        response = self.client.get(reverse('start'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Generate code for Exposure Notification app")


class CodeView(TestCase):
    def test_code(self):
        """
        Just see the code page and one code
        """
        response = self.client.get(reverse('code'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Provide patient with code")
        self.assertContains(response,
                            "<code id=\"big-code\">{}</code>".format(response.context['code']))
