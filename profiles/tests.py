from uuid import uuid4
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import translation
from django_otp import DEVICE_ID_SESSION_KEY
from invitations.models import Invitation
from .forms import SignupForm
from .models import HealthcareProvince, HealthcareUser


User = get_user_model()


def get_province(abbr="MB"):
    # Provinces are inserted into the DB during migrations, we can call them once the test DB is initialized
    return HealthcareProvince.objects.get(abbr=abbr)


def get_credentials(
    email="test@test.com",
    name="testuser",
    province=None,
    is_admin=False,
    password="testpassword",
):
    return {
        "email": email,
        "name": name,
        "province": province or get_province(),
        "is_admin": is_admin,
        "password": password,
    }


def get_other_credentials(
    email="test2@test.com",
    name="testuser2",
    province=None,
    is_admin=False,
    is_superuser=False,
    password="testpassword2",
):
    if is_superuser:
        return {
            "email": email,
            "name": name,
            "password": password,
        }

    return {
        "email": email,
        "name": name,
        "province": province or get_province(),
        "is_admin": is_admin,
        "password": password,
    }


class AdminUserTestCase(TestCase):
    def setUp(self, is_admin=False):
        self.credentials = get_credentials(is_admin=is_admin)
        self.user = User.objects.create_user(**self.credentials)
        self.credentials["username"] = self.credentials["email"]
        self.credentials["id"] = self.user.id

        self.invited_email = "invited@test.com"

    def login_2fa(self, user: HealthcareUser = None):
        if user is None:
            user = self.user

        device = user.emaildevice_set.create()
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()


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

    def test_django_admin_panel(self):
        response = self.client.get(reverse("admin:index"))
        self.assertRedirects(response, "/admin/login/?next=/admin/")


class DjangoAdminPanelView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_from_django_admin_dashboard_if_admin_user(self):
        # log in as a healthcare admin user
        self.client.login(username="test@test.com", password="testpassword")
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, "/admin/login/?next=/admin/")

    def test_see_django_admin_dashboard_if_superuser(self):
        superuser = User.objects.create_superuser(
            **get_other_credentials(is_superuser=True)
        )
        # log in as superuser
        self.client.login(username=superuser.email, password="testpassword2")

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django administration")

    @override_settings(AXES_ENABLED=True)
    def test_user_lockout(self):
        post_data = {
            "username": self.user.email,
            "password": uuid4(),
        }

        for i in range(0, settings.AXES_FAILURE_LIMIT - 1):
            response = self.client.post(
                reverse("admin:login"),
                post_data,
                REMOTE_ADDR="127.0.0.1",
                HTTP_USER_AGENT="test-browser",
            )
            self.assertContains(
                response, "Please enter the correct email address and password"
            )

        response = self.client.post(
            reverse("admin:login"),
            post_data,
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="test-browser",
        )
        self.assertEqual(response.status_code, 403)


class AuthenticatedView(AdminUserTestCase):
    def test_loginpage(self):
        #  Get the login page
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Log in</h1>")
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

        self.province = get_province()

    def test_email_in_form(self):
        f = SignupForm(initial={"email": self.invite.email})
        self.assertTrue(self.email in f.as_table())

    def test_province_in_form(self):
        f = SignupForm(initial={"province": self.province.name})
        self.assertTrue('value="Manitoba"' in f.as_table())


class SignupFlow(AdminUserTestCase):
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
            '<input type="hidden" name="province" value="{}" disabled id="id_province">'.format(
                self.credentials["province"].abbr
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


class InviteFlow(AdminUserTestCase):
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
        self.login_2fa()
        response = self.client.get(reverse("invite"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Add an account")

    def test_see_invite_complete_page_and_message_on_page(self):
        """
        Login and see the invite page with the id of the current user in a hidden input
        """
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()
        session = self.client.session
        session["invite_email"] = self.invited_email
        session.save()

        response = self.client.get(reverse("invite_complete"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Invitation sent")
        self.assertContains(
            response, "Invitation sent to “{}”".format(self.invited_email),
        )


class ProfilesView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_on_manage_accounts_page_if_logged_out(self):
        response = self.client.get(reverse("profiles"))
        self.assertRedirects(response, "/en/login/?next=/en/profiles/")

    def test_forbidden_if_not_admin(self):
        user2 = User.objects.create_user(**get_other_credentials(is_admin=False))
        self.client.login(username=user2.email, password="testpassword2")
        self.login_2fa(user2)

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 403)

    def test_manage_accounts_link_visible_if_logged_in(self):
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<a  href="{}">Manage accounts</a>'.format(reverse("profiles"))
        )

    def test_manage_accounts_page(self):
        user2 = User.objects.create_user(**get_other_credentials(is_admin=True))
        self.client.login(username=user2.email, password="testpassword2")
        self.login_2fa(user2)

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Manage accounts</h1>")
        # Make sure the email of the first user is visible
        self.assertContains(response, self.credentials["email"])

    def test_manage_accounts_page_no_users_from_other_province(self):
        user2 = User.objects.create_user(
            **get_other_credentials(province=get_province("AB"), is_admin=True)
        )

        self.client.login(username=user2.email, password="testpassword2")
        self.login_2fa(user2)

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Manage accounts</h1>")
        # make sure email of the first user is not visible
        self.assertNotContains(response, self.credentials["email"])


class ProfileView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_on_profile_page_if_logged_out(self):
        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertRedirects(
            response, "/en/login/?next=/en/profiles/{}".format(self.credentials["id"])
        )

    def test_profile_page_visible_when_logged_in(self):
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Your profile</h1>")

    def test_profile_page_not_found_if_user_id_does_not_exist(self):
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(reverse("user_profile", kwargs={"pk": 99}))
        self.assertEqual(response.status_code, 404)

    def test_fobidden_profile_page_if_non_admin_user_viewing_other_profile(self):
        user2 = User.objects.create_user(**get_other_credentials(is_admin=False))
        # password is hashed so we can't use it
        self.client.login(username=user2.email, password="testpassword2")
        self.login_2fa(user2)

        ## get user profile of admin user created in setUp
        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_profile_page_if_superuser_viewing_other_profile(self):
        # create superuser
        superuser = User.objects.create_superuser(
            **get_other_credentials(is_superuser=True)
        )
        self.client.login(username=superuser.email, password="testpassword2")
        self.login_2fa(superuser)

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<td scope="col">{}</td>'.format(self.credentials["email"])
        )

    def test_forbidden_see_profile_page_superuser(self):
        superuser = User.objects.create_superuser(
            **get_other_credentials(is_superuser=True)
        )

        # log in as user in session
        self.client.login(username=self.user.email, password="testpassword")
        self.login_2fa(self.user)

        ## get user profile of superuser
        response = self.client.get(reverse("user_profile", kwargs={"pk": superuser.id}))
        self.assertEqual(response.status_code, 403)

    def test_view_profile_page_if_admin_user_viewing_same_province_user(self):
        user2 = User.objects.create_user(**get_other_credentials(is_admin=True))
        self.client.login(username=user2.email, password="testpassword2")
        self.login_2fa(user2)

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<td scope="col">{}</td>'.format(self.credentials["email"])
        )

    def test_forbidden_profile_page_if_admin_user_viewing_other_province_user(self):
        user2 = User.objects.create_user(
            **get_other_credentials(is_admin=True, province=get_province("AB"))
        )
        self.client.login(username=user2.email, password="testpassword2")
        self.login_2fa(user2)

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 403)


class DeleteView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_forbidden_see_delete_page_for_self(self):
        # log in as user in session
        self.client.login(username=self.user.email, password="testpassword")
        self.login_2fa(self.user)

        ## get user profile of admin user created in setUp
        response = self.client.get(reverse("user_delete", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 403)

    def test_forbidden_see_delete_page_for_superuser(self):
        superuser = User.objects.create_superuser(
            **get_other_credentials(is_superuser=True)
        )

        # log in as user in session
        self.client.login(username=self.user.email, password="testpassword")
        self.login_2fa(self.user)

        ## get user profile of superuser
        response = self.client.get(reverse("user_delete", kwargs={"pk": superuser.id}))
        self.assertEqual(response.status_code, 403)

    def test_see_delete_page_for_other_user(self):
        user2 = User.objects.create_user(**get_other_credentials(is_admin=False))

        # log in as user in session
        self.client.login(username=self.user.email, password="testpassword")
        self.login_2fa()

        ## get user profile of admin user created in setUp
        response = self.client.get(reverse("user_delete", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<p>Are you sure you want to delete testuser2’s account at “test2@test.com”?</p>",
        )
