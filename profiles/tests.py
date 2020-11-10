from uuid import uuid4
from django.apps import apps
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import translation, timezone
from django.core.exceptions import ValidationError
from django_otp import DEVICE_ID_SESSION_KEY
from invitations.models import Invitation
from axes.models import AccessAttempt
from datetime import datetime, timedelta
from freezegun import freeze_time

from .apps import ProfilesConfig
from .forms import SignupForm, HealthcarePhoneEditForm
from .models import (
    HealthcareProvince,
    HealthcareUser,
    AuthorizedDomain,
    HealthcareFailedAccessAttempt,
)
from .validators import BannedPasswordValidator
from .utils.invitation_adapter import user_signed_up

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
        "phone_number": "+12125552368",
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
            "phone_number": "+12125552368",
        }

    return {
        "email": email,
        "name": name,
        "province": province or get_province(),
        "is_admin": is_admin,
        "password": password,
        "phone_number": "+12125552368",
    }


class ProfilesConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ProfilesConfig.name, "profiles")
        self.assertEqual(apps.get_app_config("profiles").name, "profiles")


class BannedPasswordValidatorTestCase(TestCase):
    def setUp(self, is_admin=False):
        self.validator = BannedPasswordValidator()

    def test_bad_12_character_passwords(self):
        for password in ["qwertyqwerty", "111111111111", "abcdefghijkl"]:
            with self.assertRaises(ValidationError):
                self.validator.validate(password)

    def test_bad_covid_passwords(self):
        for password in ["covidpassword", "PORTALpassword", "passwordViRuS"]:
            with self.assertRaises(ValidationError):
                self.validator.validate(password)


class DefaultSuperUserTestCase(TestCase):
    def test_default_superuser_from_cds(self):
        self.credentials = get_other_credentials(is_superuser=True)
        self.user = User.objects.create_superuser(**self.credentials)
        self.assertEqual(self.user.province.name, "Canadian Digital Service")


class AdminUserTestCase(TestCase):
    def setUp(self, is_admin=False):
        self.credentials = get_credentials(is_admin=is_admin)
        self.user = User.objects.create_user(**self.credentials)
        self.credentials["username"] = self.credentials["email"]
        self.credentials["id"] = self.user.id

        self.invited_email = "invited@test.com"
        AuthorizedDomain.objects.create(domain="test.com")

    def login(self, credentials: dict = None, login_2fa: bool = True):
        if credentials is None:
            credentials = self.credentials

        self.client.login(
            username=credentials.get("email"), password=credentials.get("password")
        )
        if login_2fa:
            user = HealthcareUser.objects.get(email=credentials.get("email"))
            self.login_2fa(user)

    def login_2fa(self, user: HealthcareUser = None):
        if user is None:
            user = self.user

        # We actually don't care which device, we just need one
        device = user.notifysmsdevice_set.first()
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()


class RootView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_not_authenticated_redirects_to_login(self):
        response = self.client.get("/", follow=True)
        self.assertRedirects(response, "/en/login/?next=/en/start/")

    def test_authenticated_redirects_to_start(self):
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()
        response = self.client.get("/", follow=True)
        self.assertRedirects(response, "/en/start/")


class UnauthenticatedView(TestCase):
    def test_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Log in</h1>")
        self.assertNotContains(response, '<a href="/en/login/">Log in</a>')

    def test_quick_guide(self):
        response = self.client.get(reverse("quick_guide"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Quick guide to the portal</h1>")

    def test_privacy_page(self):
        response = self.client.get(reverse("privacy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Privacy notice for COVID Alert Portal</h1>")

    def test_terms_page(self):
        response = self.client.get(reverse("terms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Terms of use</h1>")


class RestrictedPageViews(TestCase):
    #  These should redirect us
    def test_code(self):
        response = self.client.get(reverse("key"))
        self.assertRedirects(response, "/en/login/?next=/en/key/")

    def test_start(self):
        response = self.client.get(reverse("start"))
        self.assertRedirects(response, "/en/login/?next=/en/start/")

    def test_2fa(self):
        response = self.client.get(reverse("login_2fa"))
        self.assertRedirects(response, "/en/login/?next=/en/login-2fa/")

    def test_yubikey_verify(self):
        response = self.client.get(reverse("yubikey_verify"))
        self.assertRedirects(response, "/en/login/")

    def test_django_admin_panel(self):
        response = self.client.get(reverse("admin:index"))
        self.assertRedirects(response, "/admin/login/?next=/admin/")


class UserLockoutView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def attempt_logins_return_response(self, number_of_attempts):
        post_data = {
            "username": self.user.email,
            "password": uuid4(),
        }

        for i in range(0, number_of_attempts):
            response = self.client.post(
                reverse("login"),
                post_data,
                REMOTE_ADDR="127.0.0.1",
                HTTP_USER_AGENT="test-browser",
            )
            self.assertContains(
                response, "Your username or password do not match our records"
            )

        return self.client.post(
            reverse("admin:login"),
            post_data,
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="test-browser",
        )

    @override_settings(AXES_ENABLED=True)
    def test_user_lockout(self):
        response = self.attempt_logins_return_response(settings.AXES_FAILURE_LIMIT - 1)
        self.assertEqual(response.status_code, 403)

    @override_settings(
        AXES_ENABLED=True,
        AXES_FAILURE_LIMIT=100,
        AXES_SLOW_FAILURE_LIMIT=10,
        AXES_SLOW_FAILURE_COOLOFF_TIME=5,
    )
    def test_user_slow_lockout(self):
        response = self.attempt_logins_return_response(
            settings.AXES_SLOW_FAILURE_LIMIT - 1
        )
        self.assertEqual(response.status_code, 403)

        expiry = datetime.now() + timedelta(
            days=settings.AXES_SLOW_FAILURE_COOLOFF_TIME, hours=1
        )
        with freeze_time(expiry):
            response = self.client.post(
                reverse("login"),
                {
                    "username": self.user.email,
                    "password": uuid4(),
                },
                REMOTE_ADDR="127.0.0.1",
                HTTP_USER_AGENT="test-browser",
            )
            self.assertContains(
                response, "Your username or password do not match our records"
            )


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
        self.assertEqual(response.status_code, 302)
        self.login_2fa(superuser)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "administration")

    @override_settings(AXES_ENABLED=True)
    def test_user_is_blocked(self):
        other_credentials = get_other_credentials()
        other_user = User.objects.create_user(**other_credentials)
        other_user.blocked_until = timezone.now() + timedelta(days=1)
        other_user.is_active = True
        other_user.save()

        post_data = {
            "username": other_credentials.get("email"),
            "password": other_credentials.get("password"),
        }

        response = self.client.post(
            reverse("login"),
            post_data,
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="test-browser",
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(AXES_ENABLED=True)
    def test_user_is_inactive(self):
        other_credentials = get_other_credentials()
        other_user = User.objects.create_user(**other_credentials)
        other_user.blocked_until = None
        other_user.is_active = False
        other_user.save()

        post_data = {
            "username": other_credentials.get("email"),
            "password": other_credentials.get("password"),
        }

        response = self.client.post(
            reverse("login"),
            post_data,
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="test-browser",
        )

        self.assertEqual(response.status_code, 403)


class AuthenticatedView(AdminUserTestCase):
    def test_login_page(self):
        #  Get the login page
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Log in</h1>")
        self.assertContains(response, 'autocomplete="off"')

        #  Test logging in
        response = self.client.post("/en/login/", self.credentials, follow=True)
        self.assertTrue(response.context["user"].is_active)

    def test_2fa_page(self):
        self.login(login_2fa=False)

        #  Get the 2fa page
        response = self.client.get(reverse("login_2fa"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Enter your security code</h1>")
        self.assertNotContains(response, "Your account")
        self.assertContains(response, "Log out")

    def test_login_with_uppercased_email_and_whitespace(self):
        _credentials = {
            "username": "TeST@test.com  ",
            "password": self.credentials["password"],
        }

        #  Log in with uppercase letters and trailing whitespace in email address
        response = self.client.post("/en/login/", _credentials, follow=True)
        self.assertTrue(response.context["user"].is_active)

    def test_1hour_inactivity(self):
        self.login()
        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        now = datetime.now()
        expiry = now + timedelta(seconds=settings.SESSION_COOKIE_AGE + 1)
        with freeze_time(expiry):
            response = self.client.get(reverse("start"))
            self.assertRedirects(response, "/en/login/?next=/en/start/")

    def test_1hour_with_activity(self):
        self.login()
        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        now = datetime.now()
        # 30 minutes
        expiry = now + timedelta(seconds=settings.SESSION_COOKIE_AGE / 2)
        with freeze_time(expiry):
            response = self.client.get(reverse("start"))
            self.assertEqual(response.status_code, 200)

        # 1 hour + 1 second from original request
        expiry2 = now + timedelta(seconds=settings.SESSION_COOKIE_AGE + 1)
        with freeze_time(expiry2):
            response = self.client.get(reverse("start"))
            self.assertEqual(response.status_code, 200)

        # 2h + 2 sec
        expiry3 = now + timedelta(seconds=(settings.SESSION_COOKIE_AGE * 2) + 2)
        with freeze_time(expiry3):
            response = self.client.get(reverse("start"))
            self.assertEqual(response.status_code, 302)

    def test_session_timed_out_message(self):
        self.login()
        response = self.client.get(reverse("session_timed_out"))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Your session timed out.")


class i18nTestView(TestCase):
    def test_switch_language(self):
        # Test if English is shown by default if the browser doesn't send anything
        response = self.client.get("/", follow=True)
        self.assertContains(response, "Français")

        response = self.client.get("/en/switch-language/", follow=True)
        self.assertContains(response, "English")

        response = self.client.get("/fr/switch-language/", follow=True)
        self.assertContains(response, "Français")

        response = self.client.get(reverse("privacy"))
        self.assertContains(response, "<h1>Privacy notice for COVID Alert Portal</h1>")

    def test_root_with_accept_language_header_fr(self):
        """
        Test we end up on French start page from root url if "Accept-Language" header is "fr"
        """
        client = Client(
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/fr/login/")

    def test_root_with_accept_language_header_en(self):
        """
        Test we end up on English start page from root url if "Accept-Language" header is "en"
        """
        client = Client(
            HTTP_ACCEPT_LANGUAGE="en",
        )
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/login/")

    def test_root_without_accept_language_header(self):
        """
        Test we end up on English start page from root url if no "Accept-Language" header exists
        """
        client = Client()
        response = client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/login/")

    def test_start_with_language_setting_fr(self):
        """
        Test we end up on French start page from start url "fr" is active language
        """
        translation.activate("fr")
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/fr/login/")

    def test_start_with_language_setting_en(self):
        """
        Test we end up on English start page from start url "en" is active language
        """
        translation.activate("en")
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/en/login/")


class InvitationFlow(TestCase):
    def setUp(self):
        self.email = "test@test.com"
        self.invite = Invitation.create(self.email)

        self.province = get_province()

    def test_email_in_form(self):
        f = SignupForm(initial={"email": self.invite.email})
        self.assertIn(self.email, f.as_table())

    def test_province_in_form(self):
        f = SignupForm(initial={"province": self.province.name})
        self.assertIn('value="Manitoba"', f.as_table())


class SignupView(AdminUserTestCase):
    def setUp(self):
        super().setUp()
        self.invite = Invitation.create(
            self.invited_email, inviter=self.user, sent=timezone.now()
        )

        password = uuid4()
        self.new_user_data = {
            "email": self.invited_email,
            "province": "CDS",
            "name": "Chuck Norris",
            "phone_number": "+12125552368",
            "phone_number_confirmation": "+12125552368",
            "password1": password,
            "password2": password,
        }

    def test_email_and_province_on_signup_page(self):
        session = self.client.session
        session["account_verified_email"] = self.invite.email
        session.save()

        response = self.client.get(reverse("signup"))

        # assert a disabled input with the email value exists
        self.assertContains(
            response,
            '<input type="text" name="email" value="{}" autocomplete="off" disabled id="id_email">'.format(
                self.invited_email
            ),
        )
        # assert a disabled input with the province value exists
        self.assertContains(
            response,
            '<input type="hidden" name="province" value="{}" autocomplete="off" disabled id="id_province">'.format(
                self.credentials["province"].abbr
            ),
        )

    def test_redirect_if_invitation_missing_for_email_in_session(self):
        session = self.client.session
        session["account_verified_email"] = "fake@email.com"
        session.save()

        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/en/invite/expired")

    def test_invitation_accepted_after_signup(self):
        url = reverse("invitations:accept-invite", args=[self.invite.key])
        self.client.get(url)
        # make sure invite is not accepted just by visiting the URL
        self.assertEqual(self.invite.accepted, False)
        response = self.client.post(reverse("signup"), data=self.new_user_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("signup_2fa"))
        second_step_response = self.client.post(
            reverse("signup_2fa"), data=self.new_user_data
        )
        self.assertEqual(second_step_response.status_code, 302)
        self.assertEqual(
            second_step_response.url,
            reverse("login_2fa") + "?next=" + reverse("welcome"),
        )

        # The invitation is modified in another Thread and django/python gil are not aware the object has changed.
        # So let's force a reload from the DB
        self.invite.refresh_from_db()
        self.assertEqual(self.invite.accepted, True)

    @override_settings(AXES_ENABLED=True)
    def test_login_attempts_deleted_after_signup(self):
        """
        Try to log in with a username that doesn't have an account yet.
        Once we complete the signup, those access attempts should be removed.
        """
        # Assert user account doesn't exist
        self.assertIsNone(
            HealthcareUser.objects.filter(email=self.new_user_data["email"]).first()
        )

        # Try to log in with a username that doesn't exist yet
        self.client.post(
            reverse("login"),
            {"username": self.new_user_data["email"], "password": "fake_password"},
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="test-browser",
        )

        # Assert that a login attempt records exist
        self.assertTrue(
            AccessAttempt.objects.filter(username=self.new_user_data["email"]).first(),
        )
        self.assertTrue(
            HealthcareFailedAccessAttempt.objects.filter(
                username=self.new_user_data["email"]
            ).first(),
        )

        url = reverse("invitations:accept-invite", args=[self.invite.key])
        self.client.get(url)
        response = self.client.post(reverse("signup"), data=self.new_user_data)
        self.assertEqual(response.status_code, 302)

        # Assert user account exists
        self.assertTrue(
            HealthcareUser.objects.filter(email=self.new_user_data["email"]).first(),
        )

        # Assert that no login attempt records exist
        self.assertIsNone(
            AccessAttempt.objects.filter(username=self.new_user_data["email"]).first(),
        )
        self.assertIsNone(
            HealthcareFailedAccessAttempt.objects.filter(
                username=self.new_user_data["email"]
            ).first(),
        )


class InviteView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_on_invite_page_if_logged_out(self):
        response = self.client.get(reverse("invite"))
        self.assertRedirects(response, "/en/login/?next=/en/invite/")

    def test_redirect_on_invite_complete_page_if_logged_out(self):
        response = self.client.get(reverse("invite_complete"))
        self.assertRedirects(response, "/en/login/?next=/en/invite-complete/")

    def test_see_invite_page_and_inviter_id_in_form(self):
        """
        Login and see the invite page with the id of the current user in a hidden input
        """
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()
        response = self.client.get(reverse("invite"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Add new account")

    def test_send_invitation_and_see_success_message(self):
        """
        Login, send an invite, and see the success page
        """
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.post(
            reverse("invite"), {"email": self.invited_email}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<h1>Invitation sent to {}</h1>".format(self.invited_email)
        )

    def test_send_invitation_twice_and_see_success_message(self):
        """
        Login, send an invite, and see the success page twice in a row.
        This tests we can re-send invites to the same email.
        """
        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        for i in range(2):
            response = self.client.post(
                reverse("invite"), {"email": self.invited_email}, follow=True
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(
                response, "<h1>Invitation sent to {}</h1>".format(self.invited_email)
            )

    def test_sent_invite_again_if_accepted_invite_exists_and_user_account_exists(
        self,
    ):
        """
        Login and send a duplicate invite where another invite already exists
        and there is a user account corresponding to the invited email address
        """
        other_credentials = get_other_credentials(is_admin=False)
        User.objects.create_user(**other_credentials)
        Invitation.create(
            other_credentials["email"],
            inviter=self.user,
            sent=timezone.now(),
            accepted=True,
        )

        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()
        response = self.client.post(
            reverse("invite"), {"email": other_credentials["email"]}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This email address already has a portal account."
        )

    def test_sent_invite_again_if_accepted_invite_exists_but_no_user_account_exists(
        self,
    ):
        """
        Login and send a duplicate invite where another invite already exists
        BUT there is NO user account corresponding to the invited email address
        """
        other_credentials = get_other_credentials(is_admin=False)
        Invitation.create(
            other_credentials["email"],
            inviter=self.user,
            sent=timezone.now(),
            accepted=True,
        )

        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()
        response = self.client.post(
            reverse("invite"), {"email": other_credentials["email"]}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Invitation sent to {}</h1>".format(other_credentials["email"]),
        )

    def test_send_invitation_invalid_domain(self):
        self.login()
        domain = "example.com"
        email = "email@" + domain
        response = self.client.post(reverse("invite"), {"email": email}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"You cannot invite ‘{email}’ to create an account because ‘@{domain}’ is not on the portal",
        )

    def test_send_invitation_invalid_domain_with_wildcard(self):
        self.login()
        domain = "example.com"
        email = "email@" + domain
        AuthorizedDomain.objects.create(domain="*")

        response = self.client.post(reverse("invite"), {"email": email}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Invitation sent to {}</h1>".format(email))

    def test_see_invitations_list_with_pending_invite(self):
        invitation = Invitation.create(
            email=f"{uuid4()}@{uuid4()}.com", inviter=self.user
        )
        # If we dont send the invitation, we need to fake a sent date
        invitation.sent = timezone.now()
        invitation.save()

        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(reverse("invitation_list"))
        self.assertContains(response, "<td>{}</td>".format(invitation.email))
        self.assertContains(
            response, "<strong class='tag tag--blue'>Pending</strong>", html=True
        )

    def test_see_invitations_list_with_expired_invite(self):
        invitation = Invitation.create(
            email=f"{uuid4()}@{uuid4()}.com", inviter=self.user
        )
        # Invitations expire after 24 hours
        invitation.sent = timezone.now() + timezone.timedelta(hours=-25)
        invitation.save()

        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(reverse("invitation_list"))
        self.assertContains(response, "<td>{}</td>".format(invitation.email))
        self.assertContains(
            response, "<strong class='tag tag--red'>Expired</strong>", html=True
        )

    def test_delete_invitation(self):
        invitation = Invitation.create(
            email=f"{uuid4()}@{uuid4()}.com", inviter=self.user
        )
        invitation.save()

        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(
            reverse("invitation_delete", kwargs={"pk": invitation.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_invitation_normal_user(self):
        invitation = Invitation.create(
            email=f"{uuid4()}@{uuid4()}.com", inviter=self.user
        )
        invitation.save()

        other_credentials = get_other_credentials(is_admin=False)
        other_user = User.objects.create_user(**other_credentials)
        self.client.login(
            username=other_user.email, password=other_credentials.get("password")
        )
        self.login_2fa(other_user)

        response = self.client.get(
            reverse("invitation_delete", kwargs={"pk": invitation.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_confirm_invitation_deleted(self):
        invitation = Invitation.create(
            email=f"{uuid4()}@{uuid4()}.com", inviter=self.user
        )
        # If we dont send the invitation, we need to fake a sent date
        invitation.sent = timezone.now()
        invitation.save()

        self.client.login(username="test@test.com", password="testpassword")
        self.login_2fa()

        response = self.client.get(reverse("invitation_list"))
        self.assertContains(response, "<td>{}</td>".format(invitation.email))
        self.assertContains(
            response, "<strong class='tag tag--blue'>Pending</strong>", html=True
        )

        response = self.client.post(
            reverse("invitation_delete", kwargs={"pk": invitation.id}), follow=True
        )
        self.assertContains(response, "<p>No invitations yet</p>")

    def test_throttle_invitations(self):
        self.login()
        response = self.client.get(reverse("invite"))
        self.assertEqual(response.status_code, 200)

        for i in range(settings.MAX_INVITATIONS_PER_PERIOD):
            invitation = Invitation.create(
                email=f"{uuid4()}-{i}@{uuid4()}.com", inviter=self.user
            )
            invitation.save()

        response = self.client.get(reverse("invite"))
        self.assertEqual(response.status_code, 403)

        now = datetime.now()
        expiry = now + timedelta(seconds=settings.MAX_INVITATIONS_PERIOD_SECONDS + 1)
        with freeze_time(expiry):
            response = self.client.get(reverse("invite"))
            self.assertEqual(response.status_code, 200)


class InviteErrorView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_to_login_with_expired_message_on_expired_invite(self):
        invitation = Invitation.create(email="fake@example.com", inviter=self.user)
        # Invitations expire after 24 hours
        invitation.sent = timezone.now() + timezone.timedelta(hours=-25)
        invitation.save()

        url = reverse("invitations:accept-invite", kwargs={"key": invitation.key})

        response = self.client.post(url, follow=True)
        self.assertEqual(response.request["PATH_INFO"], "/en/invite/expired")
        self.assertContains(
            response,
            "<h1>You need a new link to create an account</h1>",
            html=True,
        )

    def test_redirect_to_login_with_account_exists_message_if_invite_doesnt_exist(self):
        invitation = Invitation.create(email="fake@example.com", inviter=self.user)
        invitation_key = invitation.key
        invitation.delete()

        # invitation has been deleted
        url = reverse("invitations:accept-invite", kwargs={"key": invitation_key})

        response = self.client.post(url, follow=True)
        self.assertEqual(response.request["PATH_INFO"], "/en/login/")
        self.assertContains(
            response,
            '<li class="error">Your invitation has expired. Contact your administrator for a new invitation link.</li>',
            html=True,
        )

    def test_redirect_to_login_with_account_exists_message_if_invite_accepted(self):
        invitation = Invitation.create(
            email="fake@example.com", inviter=self.user, accepted=True
        )
        invitation.sent = timezone.now()
        invitation.save()

        url = reverse("invitations:accept-invite", kwargs={"key": invitation.key})

        response = self.client.post(url, follow=True)
        self.assertEqual(response.request["PATH_INFO"], "/en/login/")
        self.assertContains(
            response,
            '<li class="error">Account already exists for ‘fake@example.com’</li>',
            html=True,
        )


class ProfilesView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_redirect_on_manage_accounts_page_if_logged_out(self):
        response = self.client.get(reverse("profiles"))
        self.assertRedirects(response, "/en/login/?next=/en/profiles/")

    def test_forbidden_if_not_admin(self):
        staff_credentials = get_other_credentials(is_admin=False)
        User.objects.create_user(**staff_credentials)
        self.login(staff_credentials)

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 403)

    def test_manage_accounts_link_visible_if_logged_in(self):
        self.login()

        response = self.client.get(reverse("start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<a  href="{}">Manage team</a>'.format(reverse("profiles"))
        )

    def test_manage_accounts_page(self):
        admin_credentials = get_other_credentials(is_admin=True)
        User.objects.create_user(**admin_credentials)
        self.login(admin_credentials)

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Manage team</h1>")
        # Make sure the email of the first user is visible
        self.assertContains(response, self.credentials["email"])

    def test_manage_accounts_page_no_users_from_other_province(self):
        admin_ab_credentials = get_other_credentials(
            is_admin=True, province=get_province("AB")
        )
        User.objects.create_user(**admin_ab_credentials)
        self.login(admin_ab_credentials)

        response = self.client.get(reverse("profiles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Manage team</h1>")
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
        self.login()

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your account")
        self.assertContains(response, self.user.name)

    def test_profile_page_not_found_if_user_id_does_not_exist(self):
        self.login()

        response = self.client.get(reverse("user_profile", kwargs={"pk": uuid4()}))
        self.assertEqual(response.status_code, 404)

    def test_forbidden_profile_page_if_non_admin_user_viewing_other_profile(self):
        staff_credentials = get_other_credentials(is_admin=False)
        User.objects.create_user(**staff_credentials)
        self.login(staff_credentials)

        ## get user profile of admin user created in setUp
        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_profile_page_if_superuser_viewing_other_profile(self):
        superuser_credentials = get_other_credentials(is_superuser=True)
        User.objects.create_superuser(**superuser_credentials)
        self.login(superuser_credentials)

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<td colspan="2">{}</td>'.format(self.credentials["email"])
        )

    def test_forbidden_see_profile_page_superuser(self):
        self.login()

        superuser = User.objects.create_superuser(
            **get_other_credentials(is_superuser=True)
        )
        ## get user profile of superuser
        response = self.client.get(reverse("user_profile", kwargs={"pk": superuser.id}))
        self.assertEqual(response.status_code, 403)

    def test_edit_profile_page_if_admin_user_viewing_staff_same_province_user(
        self,
    ):
        self.login()

        user2 = User.objects.create_user(**get_other_credentials(is_admin=False))
        response = self.client.get(reverse("user_profile", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td colspan="2">{}</td>'.format(user2.email))
        ## edit link present
        self.assertContains(
            response, '<a href="/en/profiles/{}/edit/name">'.format(user2.id)
        )

    def test_no_edit_profile_page_if_admin_user_viewing_admin_same_province_user(
        self,
    ):
        self.login()

        user2 = User.objects.create_user(**get_other_credentials(is_admin=True))
        response = self.client.get(reverse("user_profile", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td colspan="2">{}</td>'.format(user2.email))
        ## name column takes 2 rows
        self.assertContains(response, '<td colspan="2">{}</td>'.format(user2.name))
        ## no edit link present
        self.assertNotContains(
            response, '<a href="/en/profiles/{}/edit/name">'.format(user2.id)
        )

    def test_forbidden_profile_page_if_admin_user_viewing_other_province_user(self):
        admin_ab_credentials = get_other_credentials(
            is_admin=True, province=get_province("AB")
        )
        User.objects.create_user(**admin_ab_credentials)
        self.login(admin_ab_credentials)

        response = self.client.get(
            reverse("user_profile", kwargs={"pk": self.credentials["id"]})
        )
        self.assertEqual(response.status_code, 403)

    def test_only_user_can_view_own_security_codes(self):
        self.login()
        user2 = User.objects.create_user(**get_other_credentials(is_admin=True))
        response = self.client.get(reverse("user_profile", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 200)
        ## no security codes link present
        self.assertNotContains(response, '<a href="/en/backup-codes">')


class DeleteView(AdminUserTestCase):
    def setUp(self):
        super().setUp(is_admin=True)

    def test_forbidden_see_delete_page_for_self(self):
        # log in as user in session
        self.login()

        ## get user profile of admin user created in setUp
        response = self.client.get(reverse("user_delete", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 403)

    def test_admin_forbidden_see_delete_page_for_superuser(self):
        self.login()

        superuser = User.objects.create_superuser(
            **get_other_credentials(is_superuser=True)
        )

        ## get user profile of superuser
        response = self.client.get(reverse("user_delete", kwargs={"pk": superuser.id}))
        self.assertEqual(response.status_code, 403)

    def test_admin_forbidden_see_delete_page_for_other_admin(self):
        self.login()

        admin = User.objects.create_user(
            **get_other_credentials(is_admin=True, is_superuser=False)
        )

        ## get user profile of admin
        response = self.client.get(reverse("user_delete", kwargs={"pk": admin.id}))
        self.assertEqual(response.status_code, 403)

    def test_admin_see_delete_page_for_staff_user(self):
        self.login()

        user2 = User.objects.create_user(**get_other_credentials(is_admin=False))

        response = self.client.get(reverse("user_delete", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Are you sure you want to delete the account at {}?</h1>".format(
                user2.email
            ),
        )

    def test_admin_delete_staff_user_generated_keys(self):
        user2_credentials = get_other_credentials(is_admin=False)
        user2 = User.objects.create_user(**user2_credentials)
        self.login(user2_credentials)
        response = self.client.post(reverse("key"))
        self.assertEqual(response.status_code, 200)

        self.login(get_credentials())
        response = self.client.post(reverse("user_delete", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("profiles"))

    def test_superadmin_can_see_delete_page_for_admin(self):
        superuser_credentials = get_other_credentials(is_superuser=True)
        User.objects.create_superuser(**superuser_credentials)
        self.login(superuser_credentials)

        ## get user profile of admin user
        response = self.client.get(reverse("user_delete", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Are you sure you want to delete the account at {}?</h1>".format(
                self.user.email
            ),
        )

    def test_invitation_deleted(self):
        self.login()
        user_credentials = get_other_credentials()
        Invitation.create(email=user_credentials.get("email"), inviter=self.user)
        user = User.objects.create_user(**user_credentials)

        # Delete the user with an existing invitation
        response = self.client.post(reverse("user_delete", kwargs={"pk": user.id}))
        self.assertRedirects(response, reverse("profiles"))

        count = Invitation.objects.filter(email=user_credentials.get("email")).count()
        self.assertEqual(count, 0)

        # Try to delete the user without invitation
        user = User.objects.create_user(**user_credentials)
        response = self.client.post(reverse("user_delete", kwargs={"pk": user.id}))
        self.assertRedirects(response, reverse("profiles"))


class ProfileEditView(AdminUserTestCase):
    def test_edit_name(self):
        self.login()
        # see edit name page
        response = self.client.get(
            reverse("user_edit_name", kwargs={"pk": self.user.id})
        )
        self.assertEqual(response.status_code, 200)

        # post to update name
        post_data = {"name": "Don Draper"}
        response = self.client.post(
            reverse("user_edit_name", kwargs={"pk": self.user.id}),
            post_data,
        )
        self.assertEqual(response.status_code, 302)
        user = HealthcareUser.objects.get(pk=self.user.id)
        self.assertEqual(user.name, "Don Draper")

    def test_edit_email_forbidden(self):
        self.login()
        edit_url = "/profiles/{}/edit/email".format(self.user.id)
        post_data = {"email": "don@example.com"}
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 404)

    def test_edit_someone_else_account_forbidden(self):
        # staff accounts can't edit other accounts
        self.login()
        user2 = get_other_credentials(is_admin=False)
        user2 = User.objects.create_user(**user2)

        response = self.client.get(reverse("user_edit_name", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 403)

    def test_admin_edit_staff_account(self):
        admin_credentials = get_other_credentials(is_admin=True, is_superuser=False)
        User.objects.create_user(**admin_credentials)
        self.login(admin_credentials)

        user2 = User.objects.create_user(
            **get_other_credentials(email="test3@test.com", is_admin=False)
        )

        response = self.client.get(reverse("user_edit_name", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 200)

    def test_admin_edit_staff_password_forbidden(self):
        admin_credentials = get_other_credentials(is_admin=True, is_superuser=False)
        User.objects.create_user(**admin_credentials)
        self.login(admin_credentials)

        user2 = User.objects.create_user(
            **get_other_credentials(email="test3@test.com", is_admin=False)
        )

        response = self.client.get(
            reverse("user_edit_password", kwargs={"pk": user2.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_edit_admin_account_forbidden(self):
        admin_credentials = get_other_credentials(is_admin=True, is_superuser=False)
        User.objects.create_user(**admin_credentials)
        self.login(admin_credentials)

        user2 = User.objects.create_user(
            **get_other_credentials(email="test3@test.com", is_admin=True)
        )

        response = self.client.get(reverse("user_edit_name", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 403)

    def test_edit_someone_else_account_with_admin(self):
        self.login()
        user2 = get_other_credentials(is_admin=False)
        user2 = User.objects.create_user(**user2)

        response = self.client.get(reverse("user_edit_name", kwargs={"pk": user2.id}))
        self.assertEqual(response.status_code, 403)

    def test_change_phone_number(self):
        self.login()
        post_data = {
            "phone_number": "+12125552368",
            "phone_number2": "+12125552323",
        }
        response = self.client.post(
            reverse("user_edit_phone", kwargs={"pk": self.user.id}),
            post_data,
        )
        self.assertContains(
            response,
            HealthcarePhoneEditForm.error_messages.get("phone_number_mismatch"),
        )
        number = "+12125552323"
        post_data = {
            "phone_number": number,
            "phone_number2": number,
        }
        response = self.client.post(
            reverse("user_edit_phone", kwargs={"pk": self.user.id}),
            post_data,
        )
        self.assertEqual(response.status_code, 302)
        user = HealthcareUser.objects.get(pk=self.user.id)
        self.assertEqual(user.phone_number, number)
