from django.test import TestCase
from django.urls import reverse


class RegisterView(TestCase):
    def test_start_page(self):
        response = self.client.get(reverse("register:start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Create a COVID Alert QR code for your venue</h1>",
            html=True,
        )
