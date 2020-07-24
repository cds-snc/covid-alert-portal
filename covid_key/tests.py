from profiles.tests import AdminUserTestCase
from django.urls import reverse


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

    def test_key_instructions(self):
        """
        Login and then see the key instructions view and one generated code
        """
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.get(reverse("key_instructions"))
        self.assertEqual(response.status_code, 302)

        self.login_2fa()

        response = self.client.get(reverse("key_instructions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Give patient this key</h1>")
        self.assertContains(response, "<h2>Instructions for patient</h2>")
        self.assertContains(
            response, "<code>{}</code>".format(response.context["code"])
        )
