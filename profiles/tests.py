from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import translation
from invitations.models import Invitation
from .forms import SignupForm


class HomePageView(TestCase):
    def test_start(self):
        """
        Just see the start page
        """
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Generate COVID Alert number")


class RestristedPageViews(TestCase):
    #  These should redirect us
    def test_code(self):
        response = self.client.get(reverse("code"))
        self.assertRedirects(response, "/en/login/?next=/en/code/")

    def test_start(self):
        response = self.client.get(reverse("start"))
        self.assertRedirects(response, "/en/login/?next=/en/start/")


class AuthenticatedView(TestCase):
    def setUp(self):
        self.credentials = {
            "email": "test@test.com",
            "name": "testuser",
            "password": "testpassword",
        }
        User = get_user_model()
        User.objects.create_user(**self.credentials)
        self.credentials[
            "username"
        ] = "test@test.com"  # Because username is what is posted to the login page, even if email is the username field we need to add it here. Adding it before creates an error since it's not expected as part of create_user()

    def test_loginpage(self):
        #  Get the login page
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        #  Test logging in
        response = self.client.post("/en/login/", self.credentials, follow=True)
        print(response.context["user"])
        self.assertTrue(response.context["user"].is_active)

    def test_code(self):
        """
        Login and then see the code page and one code
        """
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.get(reverse("code"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Give patient this number")
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
        self.assertEqual(response.request["PATH_INFO"], "/fr/landing/")

    def test_root_with_accept_language_header_en(self):
        """
        Test we end up on English start page from root url if "Accept-Language" header is "en"
        """
        client = Client(HTTP_ACCEPT_LANGUAGE="en",)
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/landing/")

    def test_root_without_accept_language_header(self):
        """
        Test we end up on English start page from root url if no "Accept-Language" header exists
        """
        client = Client()
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/landing/")

    def test_start_with_language_setting_fr(self):
        """
        Test we end up on French start page from start url "fr" is active language
        """
        translation.activate("fr")
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/fr/landing/")

    def test_start_with_language_setting_en(self):
        """
        Test we end up on English start page from start url "en" is active language
        """
        translation.activate("en")
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/landing/")


class InvitationFlow(TestCase):

    #  TODO: Test that once an email is signed up it can't used again
    #        Only emails with invites can signup

    def setUp(self):
        self.email = "test@test.com"
        self.invite = Invitation.create(self.email)
        self.invite_url = reverse("invitations:accept-invite", args=[self.invite.key])

    def test_email_in_form(self):
        f = SignupForm(initial={"email": self.invite.email})
        self.assertTrue(self.email in f.as_table())
