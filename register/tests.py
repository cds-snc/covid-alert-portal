from django.test import TestCase
from django.urls import reverse

from waffle.models import Switch


from .models import Registrant


class RegisterView(TestCase):
    def setUp(self):
        Switch.objects.create(name="QR_CODES", active=True)

    def test_start_page(self):
        response = self.client.get(reverse("register:start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Create a COVID Alert QR code for your venue</h1>",
            html=True,
        )

    def test_email_page(self):
        response = self.client.get(reverse("register:email"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Where should we send your poster?</h1>",
            html=True,
        )

    def test_name_page(self):
        r = Registrant.objects.create(email="test@test.com")

        response = self.client.get(reverse("register:name", kwargs={"pk": r.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>What is your name?</h1>",
            html=True,
        )

    def test_confirmation_page(self):
        email = "test@test.com"

        # add email to session
        session = self.client.session
        session["registrant_email"] = email
        session.save()

        response = self.client.get(reverse("register:confirmation"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Your request for a poster has been submitted</h1>",
            html=True,
        )
        self.assertContains(
            response,
            'Thank you. As soon as it’s ready, your poster will be emailed to <a href="mailto:{0}">{0}</a>'.format(
                email
            ),
        )
