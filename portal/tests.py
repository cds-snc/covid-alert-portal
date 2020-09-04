from django.test import TestCase
from django.conf import settings
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
        self.assertContains(response, settings.DJVERSION_VERSION)


class ValidationErrorsView(TestCase):
    def test_login_no_errors(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Log in</h1>")
        self.assertNotContains(response, "Please correct the errors on the page")
        self.assertNotContains(response, 'id="error--username"')
        self.assertNotContains(
            response,
            '<div id="error--username" class="validation-error">Enter a valid email address</div>',
        )
        self.assertNotContains(response, 'aria-describedby="error--username"')

    def test_login_with_errors(self):
        response = self.client.post(
            "/en/login/",
            {"username": "roger sterling", "password": "password1234"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Log in</h1>")
        # look for error message at the top of the page
        self.assertContains(response, "Please correct the errors on the page")
        # look for a link to the field that failed validation
        self.assertContains(response, '<a href="#id_username">')
        # look for the validation error in the form
        self.assertContains(
            response,
            '<div id="error--username" class="validation-error">Enter a valid email address</div>',
        )
        # look for the input including the id, the input value, and the "aria-describedby" attribute
        self.assertContains(
            response,
            '<input type="text" name="username" value="roger sterling" autocapitalize="none" autocomplete="off" maxlength="255" aria-describedby="error--username" required id="id_username">',
        )
