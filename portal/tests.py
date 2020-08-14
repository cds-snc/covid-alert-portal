from django.test import TestCase
from django.urls import reverse


class TextView(TestCase):
    def test_robots(self):
        response = self.client.get(reverse("robots_file"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("Content-type"), "text/plain")
        self.assertContains(response, "User-Agent: *\nDisallow: /")

    def test_status(self):
        response = self.client.get(reverse("status"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("Content-type"), "text/plain")
        self.assertContains(response, "Ok")
