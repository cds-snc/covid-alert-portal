from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import translation
from invitations.models import Invitation
from .forms import SignupForm
from .models import HealthcareProvince, HealthcareUser


def get_credentials(is_admin=False):
    # Provinces are inserted into the DB during migrations, so they are already in our tests
    province = HealthcareProvince.objects.get(abbr="MB")

    return {
        "email": "test@test.com",
        "name": "testuser",
        "province": province,
        "is_admin": is_admin,
        "password": "testpassword",
    }


class LoggedInTestCase(TestCase):
    def setUp(self, is_admin=False):
        self.credentials = get_credentials(is_admin=is_admin)
        User = get_user_model()
        self.user = User.objects.create_user(**self.credentials)
        self.credentials["username"] = self.credentials["email"]
        self.credentials["id"] = self.user.id

        self.invited_email = "invited@test.com"


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


class AuthenticatedView(LoggedInTestCase):
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


class SignupFlow(LoggedInTestCase):
    def setUp(self):
        super().setUp()
        self.invite = Invitation.create(self.invited_email, inviter=self.user)

    def test_email_and_province_on_signup_page(self):
        session = self.client.session
        session["account_verified_email"] = self.invite.email
        session.save()

        response = self.client.get(reverse("signup"))

        # assert a disabled input with the email value exists
        self.assertContains(
            response,
            '<input type="text" name="email" value="{}" required disabled id="id_email">'.format(
                self.invited_email
            ),
        )
        # assert a disabled input with the province value exists
        self.assertContains(
            response,
            '<input type="text" name="province" value="{}" required disabled id="id_province">'.format(
                self.credentials["province"].name
            ),
        )

    def test_redirect_if_invitation_missing_for_email_in_session(self):
        session = self.client.session
        session["account_verified_email"] = "fake@email.com"
        session.save()

        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/en/login/")

        # get messages without request.context: https://stackoverflow.com/a/14909727
        message_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(
            str(message_list[0]), "Invitation not found for fake@email.com"
        )


class InviteFlow(LoggedInTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_on_invite_page_if_logged_out(self):
        response = self.client.get(reverse("invite"))
        self.assertRedirects(response, "/en/login/?next=/en/invite/")

    def test_redirect_on_invite_complete_page_if_logged_out(self):
        response = self.client.get(reverse("invite_complete"))
        self.assertRedirects(response, "/en/login/?next=/en/invite_complete/")

    def test_see_invite_page_and_inviter_id_in_form(self):
        """
        Login and see the invite page with the id of the current user in a hidden input
        """
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.get(reverse("invite"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Add an account")
        self.assertContains(
            response,
            '<input type="hidden" name="inviter" value="{}" id="id_inviter">'.format(
                self.credentials["id"]
            ),
        )

    def test_see_invite_complete_page_and_message_on_page(self):
        """
        Login and see the invite page with the id of the current user in a hidden input
        """
        self.client.login(username="test@test.com", password="testpassword")
        session = self.client.session
        session["invite_email"] = self.invited_email
        session.save()

        response = self.client.get(reverse("invite_complete"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Invitation sent")
        self.assertContains(
            response, "Invitation sent to “{}”".format(self.invited_email),
        )


class ProfilesView(LoggedInTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_on_invite_page_if_logged_out(self):
        response = self.client.get(reverse("profiles"))
        self.assertRedirects(response, "/en/login/?next=/en/profiles/")

    def test_manage_accounts_link_visible_if_logged_in(self):
        self.client.login(username="test@test.com", password="testpassword")

        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<a  href="{}">Manage accounts</a>'.format(reverse("profiles"))
        )

    def test_manage_accounts_page(self):
        self.client.login(username="test@test.com", password="testpassword")

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Manage accounts</h1>")
        self.assertContains(
            response, '<td scope="col">{}</td>'.format(self.credentials["email"])
        )

