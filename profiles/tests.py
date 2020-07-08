from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import translation
from django_otp import DEVICE_ID_SESSION_KEY, oath, util
from django.test import RequestFactory
from invitations.models import Invitation
from .forms import SignupForm
from .models import HealthcareProvince, HealthcareUser


def get_credentials():
    # Provinces are inserted into the DB during migrations, so they are already in our tests
    province = HealthcareProvince.objects.get(abbr="MB")

    return {
        "email": "test@test.com",
        "name": "testuser",
        "province": province,
        "password": "testpassword",
    }


class HomePageView(TestCase):
    def test_start(self):
        """
        Just see the start page
        """
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Generate COVID Alert number")


class RestrictedPageViews(TestCase):
    #  These should redirect us
    def test_code(self):
        response = self.client.get(reverse("code"))
        self.assertRedirects(response, "/en/login/?next=/en/code/")

    def test_start(self):
        response = self.client.get(reverse("start"))
        self.assertRedirects(response, "/en/login/?next=/en/start/")

    def test_signup(self):
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, "/en/login/")


class AuthenticatedView(TestCase):

    def setUp(self):
        self.credentials = get_credentials()
        User = get_user_model()
        self.user = User.objects.create_user(**self.credentials)

        # Because username is what is posted to the login page, even if email is the username field we need to add it here. Adding it before creates an error since it's not expected as part of create_user()
        self.credentials["username"] = self.credentials["email"]

    def login_2fa(self):
        device = self.user.emaildevice_set.create()
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()

    def test_loginpage(self):
        #  Get the login page
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        #  Test logging in
        response = self.client.post("/en/login/", self.credentials, follow=True)
        self.assertTrue(response.context["user"].is_active)

    def test_code(self):
        """
        Login and then see the code page and one code
        """
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.get(reverse("code"))
        self.assertEqual(response.status_code, 302)

        self.login_2fa()

        response = self.client.get(reverse("code"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Give patient this number")
        self.assertContains(
            response, "<code>{}</code>".format(response.context["code"])
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

        self.province = HealthcareProvince.objects.get(abbr="MB")

    def test_email_in_form(self):
        f = SignupForm(initial={"email": self.invite.email})
        self.assertTrue(self.email in f.as_table())

    def test_province_in_form(self):
        f = SignupForm(initial={"province": self.province.name})
        self.assertTrue('value="Manitoba"' in f.as_table())


class SignupFlow(TestCase):
    def setUp(self):
        self.credentials = get_credentials()
        User = get_user_model()
        user = User.objects.create_user(**self.credentials)
        self.credentials["username"] = self.credentials["email"]

        self.invited_email = "invited@test.com"

        self.invite = Invitation.create(self.invited_email, inviter=user)
        self.invite_url = reverse("invitations:accept-invite", args=[self.invite.key])

    def test_email_and_province_on_signup_page(self):
        session = self.client.session
        session["account_verified_email"] = self.invite.email
        session.save()

        response = self.client.get(reverse("signup"))

        # assert a disabled input with the email value exists
        self.assertTrue(
            '<input type="text" name="email" value="{}" required disabled id="id_email">'.format(
                self.invited_email
            ),
            str(response.content),
        )
        # assert a disabled input with the province value exists
        self.assertIn(
            '<input type="text" name="province" value="{}" required disabled id="id_province">'.format(
                self.credentials["province"].name
            ),
            str(response.content),
        )

    def test_redirect_if_invitation_missing_for_email_in_session(self):
        session = self.client.session
        session["account_verified_email"] = "fake@email.com"
        session.save()

        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/en/login/")

        # get messages without request.context: https://stackoverflow.com/a/14909727
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Invitation not found for fake@email.com")
